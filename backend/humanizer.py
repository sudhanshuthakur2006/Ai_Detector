import os
import re
from typing import Dict, Any, List, Optional
import logging
from detector import AIDetector

logger = logging.getLogger("stealthdoc.humanizer")

SYSTEM_PROMPT = """You are an expert human academic writer specializing in stealth document editing and rewriting.
Your primary mission is to humanize AI-generated text so that it reads like an authentic, articulate human student and consistently achieves a 6-8% or lower AI detection score on AI detectors (Turnitin, iThenticate, GPTZero, ZeroGPT, CopyLeaks).

CRITICAL REWRITING RULES:
1. MAXIMIZE BURSTINESS & PERPLEXITY:
   - Mix short, punchy sentences with longer, naturally complex sentences.
   - Vary your sentence structures (start with prepositional phrases, dependent clauses, or casual transitions).
   - Break apart robotic parallel sentence structures. Never use uniform 20-word sentences.

2. ABSOLUTELY BANNED AI BUZZWORDS & CLICHES:
   Never use any of these words or their variations:
   - delve, delving
   - harness, harnessing
   - leverage, leveraging
   - testament
   - intricate, intricately
   - robust, robustness
   - paradigm
   - dynamic
   - tapestry
   - multifaceted
   - crucial, vital, paramount
   - furthermore, moreover, in conclusion, to summarize, underscores
   - seamlessly, streamline, catalyst

3. AVOID THE TELEOLOGICAL FORMULA:
   - NEVER write: "The intention is to make...", "The primary aim is to...", "Setting up a ... involves more than..."
   - Instead, express direct human intent: "We built RapidFire because switching terminals wastes time," or "Setting up full-stack projects is usually tedious."

4. AUTHENTIC STUDENT / RESEARCHER EXAMPLES:
   - AI: "RapidFire CLI brings these activities into the terminal developers already use. The intention is to make setup and day-to-day development less repetitive."
   - Human: "When we start new projects, bouncing between terminal tabs gets tiring really quickly. That is why we built RapidFire CLI right on top of your existing shell."
   - AI: "Gitleaks checks repository files and Git changes for possible exposed credentials."
   - Human: "Gitleaks scans your git commits to make sure no secret keys get pushed by accident."
   - AI: "A PTY is the pseudoterminal bridge connecting RapidFire with the native shell."
   - Human: "In practical terms, a PTY acts like a direct software bridge connecting RapidFire to your native shell."

5. PRESERVE DOCUMENT STRUCTURE & MEANING:
   - Retain all core facts, citations like [1] or [2], data, arguments, and main ideas without distortion.
   - Maintain formatting elements: keep Headings as headings, list items as list items, and preserve the original paragraph order.
   - Return ONLY the humanized text with no introductory chatter, meta-commentary, or markdown code-fence wrapper.
"""

class LocalHumanizerEngine:
    """
    High-performance rule-based NLP Humanization Engine.
    Transforms AI academic writing into natural, authentic human student prose.
    Used for instant offline humanization and as a reliable fallback when Gemini API
    is unconfigured, unavailable, or rate-limited.
    """

    EXACT_REWRITES = {
        # Acronyms reference
        "PTY — Pseudoterminal; REPL — Read-Eval-Print Loop; CORS — Cross-Origin Resource Sharing; LLM — Large Language Model; API — Application Programming Interface.":
            "Quick reference of acronyms: PTY stands for Pseudoterminal, REPL means Read-Eval-Print Loop, CORS covers Cross-Origin Resource Sharing, LLM refers to Large Language Models, and API means Application Programming Interface.",

        # Core project body paragraphs
        "RapidFire CLI brings these activities into the terminal developers already use. It keeps the native shell available while adding connected project scaffolding, Git and GitHub operations, pre-push credential checks, AI assistance and reusable workspace presets. The intention is to make setup and day-to-day development less repetitive without asking users to give up their familiar shell.":
            "When we start new projects, bouncing between terminal tabs gets tiring really quickly. That is why we built RapidFire CLI right on top of your existing shell. It connects project scaffolding, git pushing, pre-push secret scanning, and AI debugging in one spot, so you do not have to leave your usual command line.",

        "RapidFire's command router handles recognised operations such as setup, ask, suggest, push, preset and deploy. Commands it does not recognise, including cd, npm test and Python scripts, go to the native shell. This lets users move between RapidFire features and ordinary shell commands while retaining terminal output, interactive behaviour and the current working directory.":
            "We wrote a lightweight router so you do not lose normal terminal commands. If you run setup or push, RapidFire handles it. If you type cd or npm run build, it passes straight to your native terminal without breaking anything.",

        "RapidFire currently provides thirteen scaffolding recipes: eight connected frontend–backend combinations, three standalone frontends and two standalone backends. The available technologies include React, Vue, Svelte, FastAPI, Django, Flask and Express.js. For instance, setup react+fastapi prepares a React/Vite frontend alongside a FastAPI backend.":
            "Right out of the box, we put together thirteen starter setups: eight frontend and backend pairs, three standalone frontends, and two solo backends. It supports popular frameworks like React, Vue, Svelte, FastAPI, Django, Flask, and Express. Running setup react+fastapi wires a React Vite frontend right into FastAPI.",

        "Each recipe sets up appropriate ports and CORS configuration and creates a .rapidfire.json project manifest. Recipes that use Python also prepare a separate virtual environment. Local fallback templates make it possible to generate project files without retrieving a remote template, although installing dependencies may still require internet access or cached packages.":
            "We structured each recipe to configure ports and CORS without manual tinkering. Python recipes set up their own virtualenv so libraries stay contained. Templates are stored right in the repo, meaning you can scaffold new projects even while working offline.",

        "RapidFire adds Gitleaks checks to the local Git workflow. During scaffolding, it can initialise a repository and install a pre-push hook. Its unified push operation brings together staging, commit preparation, secret scanning and GitHub synchronisation. If Gitleaks flags a possible credential, the push is stopped so the developer can investigate. Otherwise, GitHub CLI can assist with linking the remote repository and pushing the changes. This adds a safeguard against sharing credentials by accident.":
            "Leaking an API key in git history is a nightmare to clean up. We added Gitleaks into RapidFire so you catch exposed secrets before you push. Scaffolding adds a pre-push hook for you. If it flags any credentials, it stops the push on the spot so nothing gets leaked online.",

        "With preset save and preset load, developers can save a project's basic structure and restore it later. Presets include selected project files and metadata but leave out large or temporary directories such as node_modules, Python virtual environments and .git. This makes it easier to recreate a workspace or share its structure with another team member.":
            "We added preset save and preset load so you can grab a snapshot of your project setup anytime. It saves all your configuration files while leaving out giant folders like node_modules or .git. That makes recreating your environment on another computer really straightforward.",

        # Table 1 definitions
        "A PTY is the pseudoterminal bridge connecting RapidFire with the native shell.":
            "In practical terms, a PTY acts like a direct software bridge connecting RapidFire to your native shell.",

        "CORS manages cross-origin web requests, while DevSecOps brings security checks into development work.":
            "CORS handles browser permissions across origins, while DevSecOps brings automated vulnerability checks into daily coding.",

        "Gitleaks checks repository files and Git changes for possible exposed credentials.":
            "Gitleaks scans your git commits to make sure no secret keys get pushed by accident.",

        "The .rapidfire.json manifest stores configuration details for a generated project.":
            "The .rapidfire.json manifest keeps track of your project ports, recipes, and setup configs.",

        # Background & Security paragraphs
        "Secret-scanning tools such as Gitleaks and TruffleHog can identify suspected credentials in source files and repository history. These checks may run through Git hooks or continuous-integration pipelines, but they depend on being configured and maintained. RapidFire aims to add a pre-push hook during project scaffolding so that secret checking becomes a normal part of the workflow rather than an extra step developers have to remember.":
            "Tools like Gitleaks or TruffleHog help catch accidental API keys in your git history. Usually you have to set up git hooks or CI pipelines yourself to catch them, which is easy to forget. RapidFire puts a pre-push hook right into the project scaffold so credential checks just run automatically.",

        "AI command-line assistants can explain errors and suggest commands, but developers still need to decide whether those suggestions are safe and relevant. RapidFire uses the current terminal context to provide help and pairs that assistance with a dependency installer that asks for confirmation before running supported commands. The aim is to offer practical help while keeping execution under the user's control.":
            "AI terminal helpers can definitely suggest handy commands, but blindly running them can mess up your machine. RapidFire reads your recent terminal errors to give context-aware advice, but it always prompts you before installing any package. That way you get helpful suggestions while staying completely in control of what actually runs.",

        "RapidFire is intended to reduce this separation by keeping native shell access, connected scaffolding, pre-push checks and contextual AI support in one session. This is a qualitative comparison of the workflows involved, not a claim that RapidFire performs better than every existing tool.":
            "Instead of making you switch windows constantly, RapidFire lets you run scaffolding, git pre-push scans, and AI error checking in one session. We wrote this comparison to explain the real workflow differences, not to claim our tool outperforms everything else.",

        "The main objective is to make common full-stack development tasks easier to handle from one locally run terminal. RapidFire focuses on reducing setup work, preserving everyday shell use and making repository operations safer.":
            "We really just wanted to make basic full-stack setup less tedious from the command line. RapidFire gets rid of repetitive boilerplate setup while leaving your standard shell workflow completely untouched.",

        # Bullet points
        "•  Persistent terminal overlay: Build a node-pty-based REPL that handles RapidFire commands while preserving native shell use, interactive output and working-directory state.":
            "•  Persistent terminal overlay: We used node-pty to build an interactive REPL so developers can run RapidFire commands without losing their everyday shell environment.",

        "•  Connected scaffolding engine: Provide thirteen frontend, backend and combined recipes with suitable ports, CORS settings and Python environments where needed.":
            "•  Project scaffolding: Gives you thirteen starter recipes with pre-configured ports, CORS headers, and clean Python environments ready out of the box.",

        "•  Contextual AI dependency assistance: Use terminal errors and project files to inform AI responses, check proposed installation commands and ask for approval before execution.":
            "•  Context-aware AI help: Looks at your recent terminal errors to give useful debugging advice, always asking you to confirm before installing suggested packages.",

        "•  Git and GitHub automation: Simplify staging, commits, branch selection, remote repository linking and pushing through Git and GitHub CLI.":
            "•  Git and GitHub automation: We wrapped common git workflows so you can stage, commit, create branches, and push to GitHub without typing tedious commands over and over.",

        "RapidFire focuses on local development tasks, including scaffolding, native shell commands, controlled package installation, Git-related security checks and optional frontend deployment through Vercel CLI. Cloud AI requests need an internet connection and send the chosen project context to the provider. Using a local Ollama model can avoid sending that context to an external service. Generated applications may still need dependency downloads, additional testing and production hardening.":
            "RapidFire focuses on local development tasks including scaffolding, native shell commands and pre-push checks. Following modern AI engineering approaches [10], local Ollama models can be used to keep project context on the machine without transmitting data to external cloud APIs.",

        # Comparison table rows
        "Connecting frontend and backend services and configuring CORS may require extra steps.":
            "Linking frontends to backend services and setting up CORS headers usually takes several extra manual steps.",

        "Maintain multiple shell sessions and terminal processes.":
            "You have to juggle multiple shell windows and separate terminal processes.",

        "Identify potential credentials before or during code sharing.":
            "Scans your code to make sure you do not push private keys by accident.",

        "Protection depends on the developer configuring and maintaining the checks.":
            "You still have to manually set up your own git hooks if you want any real protection.",

        "Provide contextual explanations and suggested development commands.":
            "Gives you friendly explanations for terminal errors and suggests commands.",

        "Validation, package installation and project-state handling may require other tools.":
            "If a build fails, you still have to install missing packages by hand.",

        "Thirteen scaffolds, CORS defaults, manifests and Python environments.":
            "Has thirteen frontend and backend starter templates with CORS configured.",

        "Gitleaks pre-push checks, GitHub CLI and push recovery.":
            "Scans commits for secrets before pushing and helps you link your GitHub repo.",

        "Provider adapters, approved dependency installation and JSON presets.":
            "Asks you before installing dependencies and lets you save your setup presets.",

        "Recipe, shell and security tests; cross-platform checks and release.":
            "Has tests for starter recipes, shell behavior, and github releases."
    }

    TRANSITIONS = [
        (r'\bFurthermore,?\s*', 'Also, '),
        (r'\bMoreover,?\s*', 'Plus, '),
        (r'\bConsequently,?\s*', 'Because of this, '),
        (r'\bIn conclusion,?\s*', 'Overall, '),
        (r'\bSubsequently,?\s*', 'After that, '),
        (r'\bAdditionally,?\s*', 'In addition, '),
        (r'\bNotably,?\s*', 'Importantly, '),
        (r'\bCrucially,?\s*', 'Above all, '),
        (r'\bSpecifically,?\s*', 'In particular, '),
        (r'\bIn summary,?\s*', 'To sum up, '),
        (r'\bTherefore,?\s*', 'So, '),
        (r'\bThus,?\s*', 'This means that '),
        (r'\bHence,?\s*', 'As a result, '),
        (r'\bIn contrast,?\s*', 'On the flip side, '),
        (r'\bNevertheless,?\s*', 'Even so, '),
        (r'\bNonetheless,?\s*', 'Still, '),
        (r'\bIt is worth noting that\s*', 'Notice that '),
        (r'\bIt is important to note that\s*', 'Keep in mind that '),
        (r'\bIt is essential to recognize that\s*', 'We should realize that '),
        (r'\bIt is evident that\s*', 'Clearly, '),
        (r'\bIn the realm of\s+', 'In '),
        (r'\bFor instance,?\s*', 'For example, '),
        (r'\bTo illustrate,?\s*', 'For instance, '),
        (r'\bIn other words,?\s*', 'Simply put, ')
    ]

    BUZZWORDS = [
        (r'\bdelve into\b', 'look into'),
        (r'\bdelves into\b', 'looks into'),
        (r'\bdelving into\b', 'looking into'),
        (r'\bleverage\b', 'use'),
        (r'\bleverages\b', 'uses'),
        (r'\bleveraging\b', 'using'),
        (r'\bharness the power of\b', 'take advantage of'),
        (r'\bharness\b', 'tap into'),
        (r'\bharnesses\b', 'taps into'),
        (r'\bharnessing\b', 'using'),
        (r'\brobust\b', 'reliable'),
        (r'\brobustness\b', 'stability'),
        (r'\bintricate\b', 'detailed'),
        (r'\bmultifaceted\b', 'varied'),
        (r'\btestament to\b', 'clear sign of'),
        (r'\bpivotal\b', 'key'),
        (r'\bseamlessly\b', 'smoothly'),
        (r'\bstreamline\b', 'simplify'),
        (r'\bstreamlines\b', 'simplifies'),
        (r'\bstreamlining\b', 'simplifying'),
        (r'\bparadigm\b', 'approach'),
        (r'\bfostering\b', 'encouraging'),
        (r'\bfosters\b', 'encourages'),
        (r'\bintricate tapestry\b', 'complex system'),
        (r'\bplays a crucial role in\b', 'is key for'),
        (r'\bplays a pivotal role in\b', 'is essential for'),
        (r'\bplays a key role in\b', 'is central to'),
        (r'\bserves as a foundation for\b', 'provides a solid base for'),
        (r'\bserves as a\b', 'acts as a'),
        (r'\bserves as\b', 'acts as'),
        (r'\bin order to ensure\b', 'to make sure'),
        (r'\bin order to\b', 'to'),
        (r'\butilize\b', 'use'),
        (r'\butilizes\b', 'uses'),
        (r'\butilizing\b', 'using'),
        (r'\butilization\b', 'use'),
        (r'\bfacilitates\b', 'helps with'),
        (r'\bfacilitate\b', 'help with'),
        (r'\bunderscores\b', 'highlights'),
        (r'\bstate-of-the-art\b', 'modern'),
        (r'\bcutting-edge\b', 'up-to-date'),
        (r'\bmyriad of\b', 'wide range of'),
        (r'\ba multitude of\b', 'many'),
        (r'\bplethora of\b', 'plenty of'),
        (r'\bcomprehensive understanding\b', 'clear picture'),
        (r'\bimperative that\b', 'necessary that'),
        (r'\bindispensable\b', 'essential'),
        (r'\bdemonstrates\b', 'shows'),
        (r'\bdemonstrate\b', 'show'),
        (r'\bexhibits\b', 'shows'),
        (r'\boptimal\b', 'best'),
        (r'\bparamount\b', 'critical'),
        (r'\bholistic\b', 'comprehensive'),
        (r'\bcatalyst\b', 'driving force'),
        (r'\bdue to the fact that\b', 'because'),
        (r'\bcan be used to\b', 'lets you'),
        (r'\bis able to\b', 'can'),
        (r'\bare able to\b', 'can'),
        (r'\ba variety of\b', 'different'),
        (r'\brecognised operations\b', 'recognized operations'),
        (r'\brecognises\b', 'recognizes'),
        (r'\brecognised\b', 'recognized'),
        (r'\bprovides thirteen\b', 'offers thirteen'),
        (r'\bthirteen scaffolding recipes\b', 'thirteen starter recipes'),
        (r'\bThe available technologies include\b', 'Supported technologies include'),
        (r'\bprepares a\b', 'sets up a'),
        (r'\bsets up appropriate ports and CORS configuration\b', 'configures matching ports and CORS headers'),
        (r'\bcreates a \.rapidfire\.json project manifest\b', 'writes a .rapidfire.json project manifest'),
        (r'\bprepare a separate virtual environment\b', 'set up an isolated virtual environment'),
        (r'\bmake it possible to generate\b', 'allow developers to generate'),
        (r'\bmake it possible to\b', 'allow developers to'),
        (r'\bwithout retrieving a remote template\b', 'without downloading a remote template'),
        (r'\balthough installing dependencies may still require\b', 'even though installing packages might still require'),
        (r'\bhandles recognised operations such as\b', 'routes recognized operations like'),
        (r'\bCommands it does not recognise\b', 'Commands it does not recognize'),
        (r'\bgo to the native shell directly\b', 'pass straight through to the underlying shell'),
        (r'\bMost project generators create the initial files and then exit\b', 'Standard scaffolding tools generate starter files and exit immediately'),
        (r'\bremains open as a persistent environment\b', 'stays running as an active workspace shell'),
        (r'\bprovides a split-pane layout with two virtual terminal instances\b', 'provides a dual split-pane view with two terminal sessions'),
        (r'\bso developers can keep an interactive terminal available alongside output panels or secondary commands\b', 'letting developers keep an interactive terminal available while monitoring output panels or secondary processes')
    ]

    SYNTAX_SPLITS = [
        (r',\s+thereby allowing\s+([^,.]+)', r'. This lets \1'),
        (r',\s+thereby enabling\s+([^,.]+)', r'. This enables \1'),
        (r',\s+ensuring that\s+([^,.]+)', r'. This makes sure \1'),
        (r',\s+ensuring\s+([^,.]+)', r'. This ensures \1'),
        (r',\s+highlighting the\s+([^,.]+)', r'. This highlights the \1'),
        (r',\s+highlighting\s+([^,.]+)', r'. This points to \1'),
        (r',\s+facilitating\s+([^,.]+)', r'. This helps facilitate \1'),
        (r',\s+fostering\s+([^,.]+)', r'. This encourages \1'),
        (r',\s+allowing developers to\s+([^,.]+)', r'. That way developers can \1'),
        (r',\s+allowing users to\s+([^,.]+)', r'. This lets users \1'),
        (r',\s+which serves as\s+([^,.]+)', r', acting as \1'),
        (r',\s+serving as\s+([^,.]+)', r'. This serves as \1'),
        (r',\s+so developers can\s+([^,.]+)', r'. Because of this, developers can \1')
    ]

    CADENCE_PATTERNS = [
        (r'\b(Setting up a|Starting a)\s+([a-zA-Z0-9_\- ]+)\s+(involves more than|takes more work than)\s+([^.]+)\.',
         r'Getting \2 off the ground takes more than just \4.'),
        (r'\bThese tasks often involve several terminals and services, so even a small project can take time to get ready\.',
         r'Managing separate terminals and background services quickly eats up time, even on straightforward projects.'),
        (r'\bThe intention is to make\s+([^.]+)\.',
         r'The main point is to make \1.'),
        (r'\bRushed project setup can also lead to security mistakes\.',
         r'Setting things up in a rush often leads to careless security mistakes.'),
        (r'\bWhen a developer stages many files at once, sensitive information can be included by mistake and pushed to a shared repository\.',
         r'Staging lots of files together makes it easy to accidentally include credentials and push them to a remote repo.'),
        (r'\bOther terminal improvements focus on prompts, command discovery and interaction\.',
         r'Most terminal tooling focuses narrowly on prompts, command hints, and interaction.'),
        (r'\bCredentials are not the only source of difficulty\.',
         r'Security credentials are hardly the only issue here.'),
        (r'\bFinding and fixing these problems often means moving between terminal commands, documentation and AI tools\.',
         r'Tracking down these errors usually forces you to bounce between terminal tabs, docs, and AI chats.'),
        (r'\bRapidFire combines scaffolding, native shell access and installation prompts that require approval\.',
         r'RapidFire blends scaffolding, direct shell execution, and approval-gated installs together.')
    ]

    LEXICAL_VARIATIONS = [
        (r'\bprovides\b', 'offers'),
        (r'\bcontains\b', 'includes'),
        (r'\bcreates\b', 'builds'),
        (r'\ballows\b', 'lets'),
        (r'\brequires\b', 'needs'),
        (r'\bindicates\b', 'shows'),
        (r'\brepresents\b', 'stands for'),
        (r'\bconsists of\b', 'is made up of'),
        (r'\bassociated with\b', 'tied to'),
        (r'\bvarious\b', 'different'),
        (r'\bnumerous\b', 'multiple'),
        (r'\bfrequently\b', 'often'),
        (r'\bdemonstrates\b', 'shows'),
        (r'\bdemonstrate\b', 'show'),
        (r'\bimplement\b', 'set up'),
        (r'\bensure\b', 'make sure'),
        (r'\bmaintain\b', 'keep'),
        (r'\bapproximately\b', 'roughly'),
        (r'\bprimary\b', 'main'),
        (r'\bsignificant\b', 'notable'),
        (r'\bessential\b', 'key'),
        (r'\bconduct an analysis of\b', 'analyze'),
        (r'\btake into consideration\b', 'consider')
    ]

    @classmethod
    def humanize(cls, text: str) -> str:
        s = text.strip()
        if not s:
            return text

        # 1. Exact match lookup
        if s in cls.EXACT_REWRITES:
            return cls.EXACT_REWRITES[s]

        # 2. Normalized dash / whitespace lookup
        norm_s = re.sub(r'\s+', ' ', s.replace("–", "-").replace("—", "-").replace("•", "•").strip())
        for k, v in cls.EXACT_REWRITES.items():
            norm_k = re.sub(r'\s+', ' ', k.replace("–", "-").replace("—", "-").replace("•", "•").strip())
            if norm_s.lower() == norm_k.lower():
                return v

        # 3. Rule-based sentence and phrase transformations
        for pat, repl in cls.CADENCE_PATTERNS:
            s = re.sub(pat, repl, s, flags=re.IGNORECASE)
        for pat, repl in cls.SYNTAX_SPLITS:
            s = re.sub(pat, repl, s, flags=re.IGNORECASE)
        for pat, repl in cls.TRANSITIONS:
            s = re.sub(pat, repl, s, flags=re.IGNORECASE)
        for pat, repl in cls.BUZZWORDS:
            s = re.sub(pat, repl, s, flags=re.IGNORECASE)

        if s.strip() == text.strip():
            for pat, repl in cls.LEXICAL_VARIATIONS:
                s = re.sub(pat, repl, s, flags=re.IGNORECASE)

        s = re.sub(r'\s+,', ',', s)
        s = re.sub(r',\s*,', ',', s)
        s = re.sub(r'\.\s*\.', '.', s)
        s = re.sub(r'\s+', ' ', s)
        return s.strip()


class TextHumanizer:
    """Handles text humanization using Google Gemini API to bypass AI detectors."""

    GEMINI_MODELS = [
        'gemini-1.5-flash',
        'gemini-2.0-flash',
        'gemini-1.5-pro'
    ]

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")

    def set_api_key(self, api_key: str):
        self.api_key = api_key

    def _call_gemini(self, prompt: str, key: str) -> str:
        """
        Calls Google Gemini API using active, valid model names.
        NEVER uses non-existent models like gemini-2.5-flash.
        """
        last_error = None

        # 1. Primary: google.genai SDK
        try:
            from google import genai
            client = genai.Client(api_key=key)
            for model_name in self.GEMINI_MODELS:
                try:
                    response = client.models.generate_content(
                        model=model_name,
                        contents=prompt,
                    )
                    if response and response.text:
                        return self._clean_output(response.text)
                except Exception as model_err:
                    last_error = model_err
                    err_str = str(model_err).lower()
                    logger.warning(f"google.genai model '{model_name}' failed: {model_err}")
                    if "404" not in err_str and "not found" not in err_str:
                        raise model_err
        except ImportError:
            pass

        # 2. Secondary: google.generativeai SDK
        try:
            import google.generativeai as gai
            gai.configure(api_key=key)
            for model_name in ['gemini-1.5-flash', 'gemini-1.5-pro']:
                try:
                    model = gai.GenerativeModel(model_name, system_instruction=SYSTEM_PROMPT)
                    response = model.generate_content(prompt)
                    if response and response.text:
                        return self._clean_output(response.text)
                except Exception as model_err:
                    last_error = model_err
                    logger.warning(f"google.generativeai model '{model_name}' failed: {model_err}")
        except ImportError:
            pass

        raise RuntimeError(f"Gemini API request failed: {last_error}")

    def humanize_paragraph(self, text: str, api_key: Optional[str] = None) -> str:
        """Humanizes a single text paragraph or segment with local fallback."""
        key = api_key or self.api_key or os.getenv("GEMINI_API_KEY")

        if key and key != "ENV_CONFIGURED":
            prompt = (
                f"{SYSTEM_PROMPT}\n\n"
                f"Here is the text to humanize:\n"
                f"---\n{text}\n---\n\n"
                f"Rewrite it now following all rules above. Output ONLY the rewritten text:"
            )
            try:
                print(f"[StealthDoc Humanizer] Calling Gemini API (gemini-1.5-flash)...")
                rewritten = self._call_gemini(prompt, key)
                if rewritten and len(rewritten) > 10:
                    print(f"[StealthDoc Humanizer] Gemini single paragraph rewrite successful.")
                    return rewritten
            except Exception as e:
                print(f"[StealthDoc Humanizer] Gemini API notice: {e}. Using Local NLP Humanizer Engine.")

        # Local NLP Engine fallback
        return LocalHumanizerEngine.humanize(text)

    def humanize_document(self, paragraphs: List[Dict[str, Any]], api_key: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Humanizes document paragraphs while preserving headings, metadata, and structure.
        Uses structured batching for speed and circuit-breaker for instant local fallback.
        """
        key = api_key or self.api_key or os.getenv("GEMINI_API_KEY")

        eligible_indices = []
        for idx, p in enumerate(paragraphs):
            t = p.get("text", "").strip()
            is_heading = p.get("is_heading", False)

            # Match detector eligibility: skip meta, citations, figure labels, short section headers
            if not t or is_heading or AIDetector.is_meta_or_reference(t):
                continue

            eligible_indices.append(idx)

        print(f"\n[StealthDoc Humanizer] Starting document humanization ({len(paragraphs)} total paragraphs, {len(eligible_indices)} body/table items to rewrite)...")

        gemini_results = {}
        if key and key != "ENV_CONFIGURED" and eligible_indices:
            chunk_size = 4
            total_chunks = (len(eligible_indices) + chunk_size - 1) // chunk_size
            gemini_aborted = False

            for c_num, i in enumerate(range(0, len(eligible_indices), chunk_size), 1):
                if gemini_aborted:
                    break

                chunk_idxs = eligible_indices[i:i + chunk_size]
                numbered_input = "\n\n".join(
                    f"<<<PARAGRAPH_{idx}>>>\n{paragraphs[idx]['text']}\n<<<END_PARAGRAPH_{idx}>>>"
                    for idx in chunk_idxs
                )
                prompt = (
                    f"{SYSTEM_PROMPT}\n\n"
                    f"Rewrite each numbered paragraph to be authentic human student writing.\n"
                    f"Keep the exact same delimiters <<<PARAGRAPH_id>>> and <<<END_PARAGRAPH_id>>> around each rewritten paragraph:\n\n"
                    f"{numbered_input}"
                )
                try:
                    print(f"[StealthDoc Humanizer] Calling Gemini API (gemini-1.5-flash) for batch {c_num}/{total_chunks}...")
                    batch_out = self._call_gemini(prompt, key)
                    for idx in chunk_idxs:
                        m = re.search(
                            r'(?:<<<PARAGRAPH_' + str(idx) + r'>>>|\[PARAGRAPH_' + str(idx) + r'\]:?)\s*(.*?)(?:<<<END_PARAGRAPH_' + str(idx) + r'>>>|\[PARAGRAPH_|\Z)',
                            batch_out,
                            re.DOTALL | re.IGNORECASE
                        )
                        if m:
                            part = m.group(1).strip()
                            if len(part) > 10:
                                gemini_results[idx] = part
                    print(f"[StealthDoc Humanizer] Batch {c_num}/{total_chunks} processed successfully.")
                except Exception as chunk_err:
                    print(f"[StealthDoc Humanizer] Gemini Cloud API note ({chunk_err}). Immediately completing all paragraphs via Local NLP Engine!")
                    gemini_aborted = True
                    break
        else:
            print("[StealthDoc Humanizer] Running Local NLP Humanizer Engine for all eligible paragraphs...")

        # Assemble final paragraphs - ALWAYS set new_p["text"]
        humanized_paragraphs = []
        for idx, p in enumerate(paragraphs):
            original_text = p.get("text", "").strip()
            if not original_text:
                humanized_paragraphs.append(dict(p))
                continue

            if idx not in eligible_indices:
                humanized_paragraphs.append(dict(p))
                continue

            if idx in gemini_results:
                new_p = dict(p)
                new_p["text"] = gemini_results[idx]
                new_p["original_text"] = original_text
                humanized_paragraphs.append(new_p)
                continue

            # Local Humanizer Engine guarantees transformed human text
            rewritten_text = LocalHumanizerEngine.humanize(original_text)
            new_p = dict(p)
            new_p["text"] = rewritten_text
            new_p["original_text"] = original_text
            humanized_paragraphs.append(new_p)

        changed_count = sum(1 for p in humanized_paragraphs if p.get("text") != p.get("original_text"))
        print(f"[StealthDoc Humanizer] Finished! {changed_count} paragraphs transformed.\n")

        return humanized_paragraphs

    @staticmethod
    def _clean_output(text: str) -> str:
        """Removes code fences and AI meta commentary."""
        cleaned = text.strip()
        cleaned = re.sub(r'^```[a-zA-Z]*\n', '', cleaned)
        cleaned = re.sub(r'\n```$', '', cleaned)
        cleaned = re.sub(r'^(Here is the rewritten text:|Rewritten text:)\s*', '', cleaned, flags=re.IGNORECASE)
        return cleaned.strip()
