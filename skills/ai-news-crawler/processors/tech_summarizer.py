"""
Technology-focused summarizer with LLM support for developers
Uses claude code CLI instead of direct API calls
"""
import os
import json
import subprocess
from typing import List, Dict, Any, Tuple, Optional
from collections import Counter
import re


class TechSummarizer:
    """Generate technology-focused summaries using LLM or rule-based fallback"""

    def __init__(self, llm_client=None):
        """
        Initialize summarizer

        Args:
            llm_client: Optional LLM client (e.g., anthropic.Anthropic) for AI summaries
        """
        self.llm_client = llm_client
        self.tech_keywords = {
            "llm": ["gpt", "claude", "llama", "gemini", "mistral", "transformer"],
            "architecture": ["moe", "mixture of experts", "diffusion", "gan", "vae"],
            "technique": ["rag", "fine-tuning", "prompt", "chain-of-thought", "rlhf"],
            "infra": ["deployment", "inference", "quantization", "distillation"],
            "code": ["github", "open source", "implementation", "code"]
        }

    def summarize(
        self,
        articles: List[Dict[str, Any]],
        use_llm: bool = True,
        llm_provider: str = "anthropic"
    ) -> Tuple[str, Dict[str, str], List[Dict[str, Any]], List[str]]:
        """
        Generate tech-focused summaries

        Args:
            articles: List of article dictionaries
            use_llm: Whether to use LLM for deep summaries
            llm_provider: LLM provider name (anthropic, openai, etc.)

        Returns:
            (overall_summary, category_summaries, articles_with_brief, key_takeaways)
        """
        # Always generate basic stats
        cat_counts = Counter([a.get("dev_category", "other") for a in articles])

        # Generate brief for each article
        articles = self._generate_briefs(articles)

        # Generate key takeaways
        key_takeaways = self._generate_key_takeaways(articles, cat_counts)

        # Try LLM summary first if enabled
        if use_llm and self._can_use_llm(llm_provider):
            try:
                overall, cat_summaries = self._generate_llm_summaries(articles, cat_counts, llm_provider)
                return overall, cat_summaries, articles, key_takeaways
            except Exception as e:
                print(f"  [Summarizer] LLM failed: {e}, using fallback")

        # Fallback to rule-based summary
        overall, cat_summaries = self._generate_rule_based_summaries(articles, cat_counts)
        return overall, cat_summaries, articles, key_takeaways

    def _generate_briefs(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate one-sentence highlight brief for each article"""
        for article in articles:
            if not article.get("brief"):
                article["brief"] = self._create_brief(article)
        return articles

    def _create_brief(self, article: Dict[str, Any]) -> str:
        """Create a one-sentence highlight brief for an article"""
        title = article.get("title", "")
        summary = article.get("summary", "")
        category = article.get("dev_category", "")
        source = article.get("source", "")

        # GitHub projects - focus on what it does and its popularity
        if category == "code" or "github" in source.lower():
            stars = article.get("stars", 0)
            stars_today = article.get("stars_today", 0)
            lang = article.get("language", "")

            # Extract key capability from summary
            desc = summary[:80] if summary else ""
            if stars_today and stars_today > 0:
                return f"今日新增 {stars_today}★ | {lang} 项目：{desc}..." if lang else f"今日新增 {stars_today}★：{desc}..."
            elif stars and stars > 1000:
                return f"{stars//1000}k+ Star {lang} 项目：{desc}..." if lang else f"{stars//1000}k+ Star 项目：{desc}..."
            else:
                return f"值得关注：{desc}..."

        # ArXiv papers - focus on innovation
        if category == "paper" or "arxiv" in source.lower():
            # Extract key innovation from title
            highlights = article.get("metadata", {}).get("tech_highlights", [])
            if highlights:
                return f"技术创新：{highlights[0]}"

            # Look for key terms in title
            key_terms = ["novel", "efficient", "scalable", "new", "improved", "faster", "better"]
            title_lower = title.lower()
            for term in key_terms:
                if term in title_lower:
                    return f"{term.title()}方法：{title[:60]}..."

            return f"前沿研究：{title[:60]}..."

        # Tools - focus on utility
        if category == "tool":
            return f"开发者工具：{summary[:70]}..." if summary else f"实用工具：{title[:60]}"

        # Infrastructure - focus on performance/deployment
        if category == "infra":
            return f"基础设施：{summary[:70]}..." if summary else f"部署优化：{title[:60]}"

        # Default: extract key insight from summary
        if summary:
            # Try to find the first complete sentence
            sentences = re.split(r'[.!?。！？]', summary)
            for sent in sentences:
                sent = sent.strip()
                if len(sent) > 20 and len(sent) < 120:
                    return sent[:100] + "..." if len(sent) > 100 else sent

        return f"{title[:80]}..."

    def _generate_key_takeaways(self, articles: List[Dict], cat_counts: Counter) -> List[str]:
        """Generate 3 key takeaways from the articles"""
        takeaways = []

        # 1. Most important technical breakthrough (from papers or most starred repo)
        papers = [a for a in articles if a.get("dev_category") == "paper"]
        if papers:
            # Find paper with most tech highlights or first one
            top_paper = max(papers, key=lambda x: len(x.get("metadata", {}).get("tech_highlights", [])))
            highlights = top_paper.get("metadata", {}).get("tech_highlights", [])
            if highlights:
                takeaways.append(f"技术突破：{top_paper['title'][:50]}... - {highlights[0]}")
            else:
                takeaways.append(f"值得关注的研究：{top_paper['title'][:60]}...")
        else:
            # Use overall stats
            takeaways.append(f"今日共收录 {len(articles)} 篇技术内容，涵盖 {len(cat_counts)} 个领域")

        # 2. Hottest open source project
        github_items = [a for a in articles if a.get("dev_category") == "code"]
        if github_items:
            top_repo = max(github_items, key=lambda x: x.get("stars_today", 0) or 0)
            stars_today = top_repo.get("stars_today", 0)
            if stars_today > 0:
                takeaways.append(f"热门项目：{top_repo['title']} 今日新增 {stars_today} stars")
            else:
                top_by_total = max(github_items, key=lambda x: x.get("stars", 0) or 0)
                takeaways.append(f"热门项目：{top_by_total['title']} (★ {top_by_total.get('stars', 0)})")

        # 3. Trending topic or research direction
        all_tags = []
        for article in articles:
            all_tags.extend(article.get("tags", []))
        trending = Counter(all_tags).most_common(3)
        if trending:
            topics = [t[0] for t in trending]
            takeaways.append(f"热门标签：{', '.join(topics)}")

        return takeaways

    def _can_use_llm(self, provider: str = "anthropic") -> bool:
        """Check if LLM is available"""
        if provider == "anthropic":
            # Check if claude code CLI is available
            try:
                result = subprocess.run(
                    ["claude", "--version"],
                    capture_output=True,
                    timeout=5
                )
                return result.returncode == 0
            except (subprocess.TimeoutExpired, FileNotFoundError):
                return False
        elif provider == "openai":
            return bool(os.getenv("OPENAI_API_KEY"))
        return False

    def _generate_llm_summaries(
        self,
        articles: List[Dict],
        cat_counts: Counter,
        provider: str
    ) -> Tuple[str, Dict[str, str]]:
        """Generate LLM-powered deep summaries"""
        # Prepare content for LLM
        content = self._prepare_llm_context(articles)

        # Generate overall summary
        overall_prompt = self._build_overall_prompt(content)
        overall_summary = self._call_llm(overall_prompt, provider)

        # Generate category summaries
        cat_summaries = {}

        categories = {
            "github": [a for a in articles if a.get("category") == "code"],
            "papers": [a for a in articles if a.get("category") == "paper"],
            "blogs": [a for a in articles if a.get("category") in ["blog", "news"]]
        }

        for cat_name, cat_articles in categories.items():
            if cat_articles:
                cat_prompt = self._build_category_prompt(cat_name, cat_articles)
                cat_summaries[cat_name] = self._call_llm(cat_prompt, provider)

        return overall_summary, cat_summaries

    def _prepare_llm_context(self, articles: List[Dict]) -> str:
        """Prepare article content for LLM prompt"""
        lines = []

        # Group by category
        github = [a for a in articles if a.get("category") == "code"]
        papers = [a for a in articles if a.get("category") == "paper"]
        blogs = [a for a in articles if a.get("category") in ["blog", "news"]]

        if github:
            lines.append("\n=== GitHub Trending Repositories ===")
            for a in github[:15]:  # Top 15
                title = a.get("title", "")
                stars = a.get("stars", 0)
                stars_today = a.get("stars_today", 0)
                lang = a.get("language", "")
                desc = a.get("summary", "")[:100]
                lines.append(f"- {title} ({lang}) | ★{stars} (+{stars_today} today): {desc}")

        if papers:
            lines.append("\n=== ArXiv Research Papers ===")
            for a in papers[:15]:
                title = a.get("title", "")
                authors = a.get("author", "")[:50]
                cat = a.get("source", "").replace("ArXiv ", "")
                abstract = a.get("summary", "")[:150]
                lines.append(f"- [{cat}] {title} - {authors}")
                lines.append(f"  Abstract: {abstract}")

        if blogs:
            lines.append("\n=== AI Blog Posts & News ===")
            for a in blogs[:15]:
                title = a.get("title", "")
                source = a.get("source", "")
                summary = a.get("summary", "")[:120]
                lines.append(f"- [{source}] {title}: {summary}")

        return "\n".join(lines)

    def _build_overall_prompt(self, content: str) -> str:
        """Build prompt for overall trend summary"""
        return f"""作为AI领域专家，请分析以下今日AI资讯，提供一份**详细的技术趋势洞察报告**。

要求：
1. 使用中文回答
2. 从**宏观角度**总结今日AI领域的整体趋势和热点方向
3. 识别**关键主题**（如：多智能体、模型架构、工具生态、商业化等）
4. 分析**技术演进方向**和**行业动态**
5. **具体到项目名称、论文标题、关键数据**
6. 每一点用项目符号列出，保持简洁有力
7. 控制在 300-500 字

格式示例：
• **多智能体协同成为主流**：今日多个项目聚焦多智能体框架，如 xxx 实现了 xxx 功能，获得 xxx stars
• **模型架构持续创新**：xxx 论文提出了 xxx 方法，实现了 xxx% 性能提升
• **开发者工具生态繁荣**：xxx 工具简化了 xxx 流程，今日新增 xxx stars
• **企业级部署需求上升**：xxx 项目专注于 xxx 优化，解决了 xxx 痛点

数据来源：
{content}

请提供详细的技术趋势分析："""

    def _build_category_prompt(self, category: str, articles: List[Dict]) -> str:
        """Build prompt for category-specific summary"""
        content = []

        for a in articles[:10]:
            if category == "github":
                content.append(f"- {a.get('title')} ({a.get('language')}): {a.get('summary', '')[:100]}")
            elif category == "papers":
                content.append(f"- {a.get('title')}: {a.get('summary', '')[:150]}")
            else:
                content.append(f"- [{a.get('source')}] {a.get('title')}: {a.get('summary', '')[:120]}")

        content_str = "\n".join(content)

        prompts = {
            "github": f"""分析以下GitHub热门仓库，总结今日开源项目的技术趋势：

{content_str}

请用 4-6 个要点总结，具体到项目名称和数据：
• 主要技术方向（如：AI Agent框架、模型微调工具等）
• 热门项目类型及亮点
• 值得关注的新项目特性
• 编程语言分布趋势
• 今日增长最快的项目及其原因
• 对开发者的实际价值

使用中文，简洁有力，提到具体项目名：""",

            "papers": f"""分析以下ArXiv论文，总结今日学术研究热点：

{content_str}

请用 4-6 个要点总结，具体到论文标题和创新点：
• 主要研究方向（如：大模型架构、多模态、推理优化等）
• 技术创新点和突破
• 潜在应用价值和场景
• 值得关注的新方法
• 实验结果亮点（如有具体数据）
• 对产业界的启示

使用中文，简洁有力，提到具体论文标题：""",

            "blogs": f"""分析以下AI博客和资讯，总结今日行业动态：

{content_str}

请用 4-6 个要点总结：
• 重要产品发布/更新
• 行业趋势观点
• 开发者关注话题
• 技术实践分享亮点
• 值得关注的讨论

使用中文，简洁有力："""
        }

        return prompts.get(category, "")

    def _call_llm(self, prompt: str, provider: str) -> str:
        """Call LLM API"""
        if provider == "anthropic":
            return self._call_anthropic(prompt)
        elif provider == "openai":
            return self._call_openai(prompt)
        raise ValueError(f"Unsupported provider: {provider}")

    def _call_anthropic(self, prompt: str) -> str:
        """Call Claude using claude code CLI with -p flag and stream-json output"""
        try:
            # Build claude code CLI command
            args = [
                "claude",
                "-p", prompt,
                "--output-format", "text",
                "--permission-mode", "acceptEdits",
                "--max-turns", "10"
            ]

            # Add model flag if specified in env
            model = os.getenv("CLAUDE_MODEL", "")
            if model:
                args.extend(["--model", model])

            # Run claude code command
            result = subprocess.run(
                args,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )

            if result.returncode != 0:
                raise RuntimeError(f"claude code failed: {result.stderr}")

            # Return text output directly
            return result.stdout.strip()

        except subprocess.TimeoutExpired:
            raise RuntimeError("claude code command timed out after 5 minutes")
        except Exception as e:
            print(f"  [LLM] Claude CLI error: {e}")
            raise

    def _parse_stream_json(self, output: str) -> str:
        """Parse claude code --output-format stream-json output"""
        text_parts = []

        for line in output.strip().split('\n'):
            if not line:
                continue
            try:
                event = json.loads(line)
                # Extract text from assistant message events
                if event.get("type") == "assistant" and event.get("message"):
                    content = event["message"].get("content", [])
                    for item in content:
                        if item.get("type") == "text":
                            text_parts.append(item.get("text", ""))
            except json.JSONDecodeError:
                # Skip non-JSON lines
                continue

        return "".join(text_parts) if text_parts else output.strip()

    def _call_openai(self, prompt: str) -> str:
        """Call OpenAI API"""
        try:
            import openai
            client = openai.OpenAI()

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                max_tokens=1000,
                temperature=0.7,
                messages=[{"role": "user", "content": prompt}]
            )

            return response.choices[0].message.content
        except Exception as e:
            print(f"  [LLM] OpenAI error: {e}")
            raise

    def _generate_rule_based_summaries(
        self,
        articles: List[Dict],
        cat_counts: Counter
    ) -> Tuple[str, Dict[str, str]]:
        """Fallback rule-based summary generation"""
        total = len(articles)

        # Build basic overall summary
        overall = f"今日共收录 {total} 篇技术内容。"

        if cat_counts.get("paper", 0) > 0:
            overall += f"其中学术论文 {cat_counts['paper']} 篇，"
        if cat_counts.get("code", 0) > 0:
            overall += f"开源项目 {cat_counts['code']} 个，"
        if cat_counts.get("blog", 0) > 0:
            overall += f"技术博客 {cat_counts['blog']} 篇。"

        # Extract trending topics
        all_tags = []
        for article in articles:
            all_tags.extend(article.get("tags", []))
        trending = Counter(all_tags).most_common(5)

        if trending:
            topics = [t[0] for t in trending]
            overall += f"\n热门技术标签: {', '.join(topics)}。"

        # Category summaries (simplified)
        cat_summaries = {}

        github_items = [a for a in articles if a.get("category") == "code"]
        if github_items:
            cat_summaries["github"] = self._summarize_github_simple(github_items)

        paper_items = [a for a in articles if a.get("category") == "paper"]
        if paper_items:
            cat_summaries["papers"] = self._summarize_papers_simple(paper_items)

        blog_items = [a for a in articles if a.get("category") in ["blog", "news"]]
        if blog_items:
            cat_summaries["blogs"] = self._summarize_blogs_simple(blog_items)

        return overall, cat_summaries

    def _summarize_github_simple(self, articles: List[Dict]) -> str:
        """Simple GitHub summary"""
        langs = Counter([a.get("language", "Unknown") for a in articles]).most_common(3)
        lang_str = ", ".join([f"{l[0]}({l[1]})" for l in langs])

        top_repo = max(articles, key=lambda x: x.get("stars_today", 0) or 0)
        top_name = top_repo.get("title", "Unknown")
        top_stars = top_repo.get("stars_today", 0)

        return f"今日GitHub热门项目涉及 {lang_str} 等语言。最热门的是 {top_name}，新增 {top_stars} stars。"

    def _summarize_papers_simple(self, articles: List[Dict]) -> str:
        """Simple papers summary"""
        cats = Counter([a.get("source", "Unknown").replace("ArXiv ", "") for a in articles]).most_common(3)
        cat_str = ", ".join([c[0] for c in cats])
        return f"今日收录 {len(articles)} 篇论文，主要来自 {cat_str} 等领域。"

    def _summarize_blogs_simple(self, articles: List[Dict]) -> str:
        """Simple blogs summary"""
        sources = Counter([a.get("source", "Unknown") for a in articles]).most_common(3)
        source_str = ", ".join([s[0] for s in sources])
        return f"今日AI博客资讯来自 {source_str} 等来源，涵盖行业动态和技术实践。"


def generate_ai_summary(articles: List[Dict[str, Any]]) -> str:
    """
    Convenience function to generate AI summary using claude code CLI

    Args:
        articles: List of articles

    Returns:
        AI-generated summary string
    """
    summarizer = TechSummarizer()
    overall, _, _ = summarizer.summarize(articles, use_llm=True)
    return overall
