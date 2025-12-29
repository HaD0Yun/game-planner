"""
html_template.py - HTML Template Generation for Game Design Documents

This module provides functions to convert GameDesignDocument models into
beautifully styled HTML documents with a dark theme and neon accents.

Usage:
    from html_template import gdd_to_html
    from models import GameDesignDocument

    gdd = GameDesignDocument(...)
    html = gdd_to_html(gdd)
"""

from __future__ import annotations

import html

from models import GameDesignDocument


def _escape(text: str) -> str:
    """Escape HTML special characters."""
    return html.escape(str(text))


def _generate_css() -> str:
    """Generate the embedded CSS styles."""
    return """
        :root {
            --bg-primary: #0f0f1a;
            --bg-secondary: #1a1a2e;
            --bg-card: #16213e;
            --accent: #e94560;
            --accent-secondary: #0f3460;
            --text-primary: #eaeaea;
            --text-secondary: #a0a0a0;
            --neon-blue: #00d9ff;
            --neon-green: #06d6a0;
            --neon-orange: #ef8354;
            --warning: #e63946;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            line-height: 1.7;
        }
        
        /* Hero Section */
        .hero {
            background: linear-gradient(135deg, var(--bg-secondary) 0%, var(--accent-secondary) 100%);
            padding: 80px 20px;
            text-align: center;
            position: relative;
            overflow: hidden;
        }
        
        .hero::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.03'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
        }
        
        .hero-content {
            position: relative;
            z-index: 1;
        }
        
        .hero h1 {
            font-size: 4rem;
            font-weight: 800;
            margin-bottom: 10px;
            background: linear-gradient(90deg, var(--neon-blue), var(--accent));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            text-shadow: 0 0 40px rgba(233, 69, 96, 0.3);
        }
        
        .hero .subtitle {
            font-size: 1.5rem;
            color: var(--text-secondary);
            margin-bottom: 30px;
        }
        
        .hero .tagline {
            font-size: 1.2rem;
            color: var(--neon-green);
            font-style: italic;
        }
        
        .badge-container {
            display: flex;
            justify-content: center;
            gap: 15px;
            margin-top: 30px;
            flex-wrap: wrap;
        }
        
        .badge {
            background: rgba(255,255,255,0.1);
            padding: 8px 20px;
            border-radius: 20px;
            font-size: 0.9rem;
            border: 1px solid rgba(255,255,255,0.2);
        }
        
        /* Navigation */
        .nav {
            background: var(--bg-secondary);
            padding: 15px 20px;
            position: sticky;
            top: 0;
            z-index: 100;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        
        .nav-content {
            max-width: 1200px;
            margin: 0 auto;
            display: flex;
            gap: 20px;
            overflow-x: auto;
            padding-bottom: 5px;
        }
        
        .nav a {
            color: var(--text-secondary);
            text-decoration: none;
            white-space: nowrap;
            padding: 5px 15px;
            border-radius: 5px;
            transition: all 0.3s;
        }
        
        .nav a:hover {
            color: var(--text-primary);
            background: rgba(255,255,255,0.1);
        }
        
        /* Main Content */
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 40px 20px;
        }
        
        section {
            margin-bottom: 60px;
        }
        
        h2 {
            font-size: 2.2rem;
            margin-bottom: 30px;
            padding-bottom: 15px;
            border-bottom: 3px solid var(--accent);
            display: flex;
            align-items: center;
            gap: 15px;
        }
        
        h2 .icon {
            font-size: 2rem;
        }
        
        h3 {
            font-size: 1.5rem;
            margin: 30px 0 20px;
            color: var(--neon-blue);
        }
        
        h4 {
            font-size: 1.2rem;
            margin: 20px 0 15px;
            color: var(--neon-orange);
        }
        
        /* Cards */
        .card {
            background: var(--bg-card);
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 20px;
            border: 1px solid rgba(255,255,255,0.1);
            transition: transform 0.3s, box-shadow 0.3s;
        }
        
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 40px rgba(233, 69, 96, 0.2);
        }
        
        .card-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }
        
        /* Tables */
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background: var(--bg-card);
            border-radius: 10px;
            overflow: hidden;
        }
        
        th, td {
            padding: 15px;
            text-align: left;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        
        th {
            background: var(--accent-secondary);
            color: var(--neon-blue);
            font-weight: 600;
        }
        
        tr:hover {
            background: rgba(255,255,255,0.05);
        }
        
        /* World Cards */
        .world-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
        }
        
        .world-card {
            background: var(--bg-card);
            border-radius: 15px;
            padding: 25px;
            border-left: 4px solid;
            transition: all 0.3s;
        }
        
        .world-card:nth-child(1) { border-color: #6c757d; }
        .world-card:nth-child(2) { border-color: #9b59b6; }
        .world-card:nth-child(3) { border-color: #2ecc71; }
        .world-card:nth-child(4) { border-color: #e74c3c; }
        .world-card:nth-child(5) { border-color: #f39c12; }
        .world-card:nth-child(6) { border-color: #00d9ff; }
        
        .world-card:hover {
            transform: scale(1.02);
        }
        
        .world-number {
            font-size: 3rem;
            font-weight: 800;
            opacity: 0.3;
            float: right;
            margin-top: -10px;
        }
        
        /* Bullet Items */
        .bullet-item {
            background: rgba(255,255,255,0.05);
            padding: 15px 20px;
            border-radius: 10px;
            margin: 10px 0;
            border-left: 3px solid var(--accent);
        }
        
        /* Core Loop Diagram */
        .core-loop {
            background: var(--bg-card);
            border-radius: 20px;
            padding: 40px;
            text-align: center;
            margin: 30px 0;
        }
        
        .loop-steps {
            display: flex;
            justify-content: center;
            align-items: center;
            flex-wrap: wrap;
            gap: 10px;
            margin-top: 20px;
        }
        
        .loop-step {
            background: var(--accent-secondary);
            padding: 15px 25px;
            border-radius: 10px;
            font-weight: 600;
        }
        
        .loop-arrow {
            color: var(--accent);
            font-size: 1.5rem;
        }
        
        /* Special Bullets */
        .special-bullet {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        
        .bullet-box {
            background: var(--bg-card);
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            border: 1px solid rgba(255,255,255,0.1);
        }
        
        .bullet-box .icon {
            font-size: 2rem;
            margin-bottom: 10px;
        }
        
        /* Timeline */
        .timeline {
            position: relative;
            padding-left: 30px;
            margin: 30px 0;
        }
        
        .timeline::before {
            content: '';
            position: absolute;
            left: 10px;
            top: 0;
            bottom: 0;
            width: 2px;
            background: var(--accent);
        }
        
        .timeline-item {
            position: relative;
            margin-bottom: 30px;
            padding-left: 20px;
        }
        
        .timeline-item::before {
            content: '';
            position: absolute;
            left: -24px;
            top: 5px;
            width: 12px;
            height: 12px;
            background: var(--accent);
            border-radius: 50%;
        }
        
        /* Characters */
        .character-card {
            display: flex;
            gap: 20px;
            background: var(--bg-card);
            border-radius: 15px;
            padding: 25px;
            margin: 20px 0;
        }
        
        .character-avatar {
            font-size: 4rem;
            min-width: 80px;
            text-align: center;
        }
        
        .character-info h4 {
            margin-top: 0;
        }
        
        .character-quote {
            font-style: italic;
            color: var(--text-secondary);
            border-left: 3px solid var(--accent);
            padding-left: 15px;
            margin-top: 15px;
        }
        
        /* Color Palette */
        .color-palette {
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
            margin: 20px 0;
        }
        
        .color-swatch {
            text-align: center;
        }
        
        .color-box {
            width: 80px;
            height: 80px;
            border-radius: 10px;
            margin-bottom: 10px;
            border: 2px solid rgba(255,255,255,0.2);
        }
        
        .color-label {
            font-size: 0.8rem;
            color: var(--text-secondary);
        }
        
        /* Footer */
        footer {
            background: var(--bg-secondary);
            padding: 40px 20px;
            text-align: center;
            border-top: 1px solid rgba(255,255,255,0.1);
        }
        
        footer p {
            color: var(--text-secondary);
            margin: 5px 0;
        }
        
        /* Responsive */
        @media (max-width: 768px) {
            .hero h1 {
                font-size: 2.5rem;
            }
            
            .hero .subtitle {
                font-size: 1.2rem;
            }
            
            h2 {
                font-size: 1.8rem;
            }
            
            .character-card {
                flex-direction: column;
                text-align: center;
            }
        }
        
        /* Animations */
        @keyframes glow {
            0%, 100% { box-shadow: 0 0 20px rgba(233, 69, 96, 0.3); }
            50% { box-shadow: 0 0 40px rgba(233, 69, 96, 0.6); }
        }
        
        .glow {
            animation: glow 2s infinite;
        }

        /* Risk badges */
        .risk-badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.8rem;
            font-weight: 600;
            margin-right: 8px;
        }
        
        .risk-critical {
            background: var(--warning);
            color: white;
        }
        
        .risk-major {
            background: var(--neon-orange);
            color: white;
        }

        /* List styles */
        ul {
            list-style: none;
            padding: 0;
        }

        ul li {
            padding: 8px 0;
            padding-left: 20px;
            position: relative;
        }

        ul li::before {
            content: '>';
            position: absolute;
            left: 0;
            color: var(--accent);
            font-weight: bold;
        }
"""


def _generate_hero_section(gdd: GameDesignDocument) -> str:
    """Generate the hero section with game title and badges."""
    title = _escape(gdd.meta.title)

    # Get elevator pitch or USP for tagline
    tagline = ""
    if gdd.meta.elevator_pitch:
        tagline = f'<p class="tagline">"{_escape(gdd.meta.elevator_pitch)}"</p>'

    # Generate badges
    badges = []
    for genre in gdd.meta.genres[:4]:  # Limit to 4 genres
        badges.append(
            f'<span class="badge">{_escape(genre.value.replace("_", " ").title())}</span>'
        )

    badges_html = "\n                ".join(badges)

    return f"""
    <!-- Hero Section -->
    <header class="hero">
        <div class="hero-content">
            <h1>{title}</h1>
            <p class="subtitle">{_escape(gdd.meta.unique_selling_point[:100])}</p>
            {tagline}
            <div class="badge-container">
                {badges_html}
            </div>
        </div>
    </header>
"""


def _generate_navigation() -> str:
    """Generate the sticky navigation bar."""
    return """
    <!-- Navigation -->
    <nav class="nav">
        <div class="nav-content">
            <a href="#meta">Overview</a>
            <a href="#core-loop">Core Loop</a>
            <a href="#systems">Systems</a>
            <a href="#progression">Progression</a>
            <a href="#narrative">Story</a>
            <a href="#characters">Characters</a>
            <a href="#tech">Technical</a>
            <a href="#risks">Risks</a>
        </div>
    </nav>
"""


def _generate_meta_section(gdd: GameDesignDocument) -> str:
    """Generate the game overview/meta section."""
    genres = ", ".join(g.value.replace("_", " ").title() for g in gdd.meta.genres)
    platforms = ", ".join(
        p.value.replace("_", " ").title() for p in gdd.meta.target_platforms
    )

    return f"""
        <!-- Meta Section -->
        <section id="meta">
            <h2><span class="icon">Overview</span></h2>
            
            <div class="card-grid">
                <div class="card">
                    <h4>Genres</h4>
                    <p><strong>{_escape(genres)}</strong></p>
                </div>
                
                <div class="card">
                    <h4>Platforms</h4>
                    <p><strong>{_escape(platforms)}</strong></p>
                </div>
                
                <div class="card">
                    <h4>Target Audience</h4>
                    <p><strong>{_escape(gdd.meta.target_audience)}</strong></p>
                    <p style="color: var(--text-secondary)">{_escape(gdd.meta.audience_rating.value.replace("_", " ").title())}</p>
                </div>
                
                <div class="card">
                    <h4>Development Time</h4>
                    <p style="font-size: 2rem; font-weight: bold; color: var(--neon-blue)">{gdd.meta.estimated_dev_time_weeks} weeks</p>
                    <p style="color: var(--text-secondary)">Team size: {gdd.meta.team_size_estimate}</p>
                </div>
            </div>
            
            <h3>Unique Selling Point</h3>
            <div class="card">
                <p style="font-size: 1.1rem">{_escape(gdd.meta.unique_selling_point)}</p>
            </div>
        </section>
"""


def _generate_core_loop_section(gdd: GameDesignDocument) -> str:
    """Generate the core loop section with diagram."""
    loop = gdd.core_loop

    # Generate loop steps
    steps_html = []
    for i, action in enumerate(loop.primary_actions):
        steps_html.append(f'<span class="loop-step">{_escape(action)}</span>')
        if i < len(loop.primary_actions) - 1:
            steps_html.append('<span class="loop-arrow">-></span>')

    steps = "\n                    ".join(steps_html)

    # Generate hook elements if present
    hooks_html = ""
    if loop.hook_elements:
        hooks_items = "".join(
            f"<li>{_escape(hook)}</li>" for hook in loop.hook_elements
        )
        hooks_html = f"""
            <h3>Hook Elements</h3>
            <div class="card">
                <ul>{hooks_items}</ul>
            </div>
"""

    return f"""
        <!-- Core Loop Section -->
        <section id="core-loop">
            <h2><span class="icon">Core Loop</span></h2>
            
            <div class="core-loop glow">
                <h3 style="margin-top: 0">Gameplay Flow</h3>
                <div class="loop-steps">
                    {steps}
                </div>
            </div>
            
            <div class="card-grid">
                <div class="card">
                    <h4>Challenge</h4>
                    <p>{_escape(loop.challenge_description)}</p>
                </div>
                <div class="card">
                    <h4>Reward</h4>
                    <p>{_escape(loop.reward_description)}</p>
                </div>
            </div>
            
            <h3>Loop Description</h3>
            <div class="card">
                <p>{_escape(loop.loop_description)}</p>
            </div>
            
            <div class="card-grid">
                <div class="card">
                    <h4>Session Length</h4>
                    <p style="font-size: 2rem; font-weight: bold; color: var(--neon-green)">{loop.session_length_minutes} min</p>
                </div>
            </div>
            {hooks_html}
        </section>
"""


def _generate_systems_section(gdd: GameDesignDocument) -> str:
    """Generate the game systems section with tables."""

    # Generate systems table rows
    rows = []
    for system in gdd.systems:
        mechanics = ", ".join(system.mechanics[:5])  # Limit mechanics shown
        rows.append(f"""
                    <tr>
                        <td><strong>{_escape(system.name)}</strong></td>
                        <td>{_escape(system.type.value.replace("_", " ").title())}</td>
                        <td>{_escape(mechanics)}</td>
                        <td>{system.priority}</td>
                    </tr>""")

    rows_html = "".join(rows)

    # Generate detailed system cards
    cards = []
    for system in gdd.systems[:6]:  # Limit to 6 systems
        mechanics_list = "".join(f"<li>{_escape(m)}</li>" for m in system.mechanics)
        cards.append(f"""
                <div class="card">
                    <h4>{_escape(system.name)}</h4>
                    <p style="color: var(--neon-blue)">{_escape(system.type.value.replace("_", " ").title())}</p>
                    <p style="margin: 15px 0">{_escape(system.description)}</p>
                    <h4 style="color: var(--text-secondary); font-size: 1rem">Mechanics</h4>
                    <ul>{mechanics_list}</ul>
                </div>""")

    cards_html = "\n            ".join(cards)

    return f"""
        <!-- Systems Section -->
        <section id="systems">
            <h2><span class="icon">Game Systems</span></h2>
            
            <table>
                <thead>
                    <tr>
                        <th>System</th>
                        <th>Type</th>
                        <th>Key Mechanics</th>
                        <th>Priority</th>
                    </tr>
                </thead>
                <tbody>
                    {rows_html}
                </tbody>
            </table>
            
            <h3>System Details</h3>
            <div class="card-grid">
                {cards_html}
            </div>
        </section>
"""


def _generate_progression_section(gdd: GameDesignDocument) -> str:
    """Generate the progression section with milestones."""
    prog = gdd.progression

    # Generate milestone timeline
    timeline_items = []
    for milestone in prog.milestones:
        timeline_items.append(f"""
                <div class="timeline-item">
                    <h4>{_escape(milestone.name)}</h4>
                    <p>{_escape(milestone.description)}</p>
                    <p style="color: var(--text-secondary)">Unlock: {_escape(milestone.unlock_condition)}</p>
                </div>""")

    timeline_html = "\n            ".join(timeline_items)

    # Generate difficulty levels if present
    difficulty_html = ""
    if prog.difficulty_levels:
        diff_cards = []
        for diff in prog.difficulty_levels:
            diff_cards.append(f"""
                    <div class="card">
                        <h4>{_escape(diff.name)}</h4>
                        <p>{_escape(diff.description)}</p>
                    </div>""")
        difficulty_html = f"""
            <h3>Difficulty Levels</h3>
            <div class="card-grid">
                {"".join(diff_cards)}
            </div>
"""

    meta_prog_html = ""
    if prog.meta_progression_description:
        meta_prog_html = f"""
            <h3>Meta Progression</h3>
            <div class="card">
                <p>{_escape(prog.meta_progression_description)}</p>
            </div>
"""

    return f"""
        <!-- Progression Section -->
        <section id="progression">
            <h2><span class="icon">Progression</span></h2>
            
            <div class="card-grid">
                <div class="card">
                    <h4>Progression Type</h4>
                    <p style="font-size: 1.5rem; font-weight: bold; color: var(--neon-blue)">{_escape(prog.type.value.replace("_", " ").title())}</p>
                </div>
                <div class="card">
                    <h4>Difficulty Curve</h4>
                    <p>{_escape(prog.difficulty_curve_description)}</p>
                </div>
            </div>
            
            <h3>Milestones</h3>
            <div class="timeline">
                {timeline_html}
            </div>
            {difficulty_html}
            {meta_prog_html}
        </section>
"""


def _generate_narrative_section(gdd: GameDesignDocument) -> str:
    """Generate the narrative/story section."""
    narrative = gdd.narrative
    themes = ", ".join(narrative.themes)
    delivery = ", ".join(
        d.value.replace("_", " ").title() for d in narrative.narrative_delivery
    )

    # Story beats timeline
    beats_html = ""
    if narrative.key_story_beats:
        beats_items = []
        for beat in narrative.key_story_beats:
            beats_items.append(f"""
                <div class="timeline-item">
                    <p>{_escape(beat)}</p>
                </div>""")
        beats_html = f"""
            <h3>Story Beats</h3>
            <div class="timeline">
                {"".join(beats_items)}
            </div>
"""

    # World lore
    lore_html = ""
    if narrative.world_lore:
        lore_html = f"""
            <h3>World Lore</h3>
            <div class="card">
                <p>{_escape(narrative.world_lore)}</p>
            </div>
"""

    return f"""
        <!-- Narrative Section -->
        <section id="narrative">
            <h2><span class="icon">Story</span></h2>
            
            <div class="card" style="border-left: 4px solid var(--accent)">
                <h3 style="margin-top: 0">Setting</h3>
                <p style="font-size: 1.1rem; line-height: 2">
                    {_escape(narrative.setting)}
                </p>
            </div>
            
            <h3>Story Premise</h3>
            <div class="card">
                <p style="font-size: 1.1rem">{_escape(narrative.story_premise)}</p>
            </div>
            
            <div class="card-grid">
                <div class="card">
                    <h4>Themes</h4>
                    <p><strong>{_escape(themes)}</strong></p>
                </div>
                <div class="card">
                    <h4>Narrative Delivery</h4>
                    <p><strong>{_escape(delivery)}</strong></p>
                </div>
                <div class="card">
                    <h4>Story Structure</h4>
                    <p>{_escape(narrative.story_structure)}</p>
                </div>
            </div>
            {beats_html}
            {lore_html}
        </section>
"""


def _generate_characters_section(gdd: GameDesignDocument) -> str:
    """Generate the characters section."""
    if not gdd.narrative.characters:
        return ""

    cards = []
    for char in gdd.narrative.characters:
        abilities_html = ""
        if char.abilities:
            abilities = ", ".join(char.abilities)
            abilities_html = f'<p style="color: var(--neon-green)">Abilities: {_escape(abilities)}</p>'

        motivation_html = ""
        if char.motivation:
            motivation_html = f"""
                    <div class="character-quote">
                        {_escape(char.motivation)}
                    </div>"""

        cards.append(f"""
            <div class="character-card">
                <div class="character-avatar">[{_escape(char.role[:3].upper())}]</div>
                <div class="character-info">
                    <h4 style="color: var(--neon-blue)">{_escape(char.name)}</h4>
                    <p><strong>Role:</strong> {_escape(char.role)}</p>
                    <p style="margin: 10px 0">{_escape(char.description)}</p>
                    {abilities_html}
                    {motivation_html}
                </div>
            </div>""")

    cards_html = "\n            ".join(cards)

    return f"""
        <!-- Characters Section -->
        <section id="characters">
            <h2><span class="icon">Characters</span></h2>
            {cards_html}
        </section>
"""


def _generate_technical_section(gdd: GameDesignDocument) -> str:
    """Generate the technical specifications section."""
    tech = gdd.technical

    technologies = ", ".join(tech.key_technologies)

    # Performance targets table
    perf_rows = ""
    if tech.performance_targets:
        for target in tech.performance_targets:
            perf_rows += f"""
                    <tr>
                        <td>{_escape(target.platform.value.replace("_", " ").title())}</td>
                        <td>{target.target_fps} FPS</td>
                        <td>{_escape(target.min_resolution)}</td>
                        <td>{target.max_ram_mb} MB</td>
                    </tr>"""

    perf_table = ""
    if perf_rows:
        perf_table = f"""
            <h3>Performance Targets</h3>
            <table>
                <thead>
                    <tr>
                        <th>Platform</th>
                        <th>Target FPS</th>
                        <th>Resolution</th>
                        <th>RAM</th>
                    </tr>
                </thead>
                <tbody>
                    {perf_rows}
                </tbody>
            </table>
"""

    # Accessibility features
    accessibility_html = ""
    if tech.accessibility_features:
        features = "".join(
            f"<li>{_escape(f)}</li>" for f in tech.accessibility_features
        )
        accessibility_html = f"""
            <h3>Accessibility Features</h3>
            <div class="card">
                <ul>{features}</ul>
            </div>
"""

    # Audio section
    audio = tech.audio
    sound_cats = ", ".join(audio.sound_categories)

    return f"""
        <!-- Technical Section -->
        <section id="tech">
            <h2><span class="icon">Technical Specifications</span></h2>
            
            <div class="card-grid">
                <div class="card">
                    <h4>Recommended Engine</h4>
                    <p style="font-size: 1.5rem; font-weight: bold">{_escape(tech.recommended_engine.value.title())}</p>
                </div>
                
                <div class="card">
                    <h4>Art Style</h4>
                    <p style="font-size: 1.5rem; font-weight: bold">{_escape(tech.art_style.value.replace("_", " ").title())}</p>
                </div>
                
                <div class="card">
                    <h4>Networking</h4>
                    <p style="font-size: 1.5rem; font-weight: bold">{"Required" if tech.networking_required else "Not Required"}</p>
                </div>
            </div>
            
            <h3>Key Technologies</h3>
            <div class="card">
                <p>{_escape(technologies)}</p>
            </div>
            
            {perf_table}
            
            <h3>Audio</h3>
            <div class="card-grid">
                <div class="card">
                    <h4>Music Style</h4>
                    <p>{_escape(audio.music_style)}</p>
                </div>
                <div class="card">
                    <h4>Sound Categories</h4>
                    <p>{_escape(sound_cats)}</p>
                </div>
                <div class="card">
                    <h4>Voice Acting</h4>
                    <p>{"Yes" if audio.voice_acting else "No"}</p>
                    <p style="color: var(--text-secondary)">Adaptive Music: {"Yes" if audio.adaptive_music else "No"}</p>
                </div>
            </div>
            {accessibility_html}
        </section>
"""


def _generate_risks_section(gdd: GameDesignDocument) -> str:
    """Generate the risks section."""
    if not gdd.risks:
        return """
        <!-- Risks Section -->
        <section id="risks">
            <h2><span class="icon">Risks</span></h2>
            <div class="card">
                <p style="color: var(--text-secondary)">No risks have been identified for this project.</p>
            </div>
        </section>
"""

    rows = []
    for risk in gdd.risks:
        severity_class = (
            "risk-critical" if risk.severity.value == "critical" else "risk-major"
        )
        rows.append(f"""
                    <tr>
                        <td><span class="risk-badge {severity_class}">{_escape(risk.severity.value.upper())}</span></td>
                        <td><strong>{_escape(risk.category)}</strong></td>
                        <td>{_escape(risk.description)}</td>
                        <td>{_escape(risk.mitigation)}</td>
                    </tr>""")

    rows_html = "".join(rows)

    return f"""
        <!-- Risks Section -->
        <section id="risks">
            <h2><span class="icon">Risks</span></h2>
            
            <table>
                <thead>
                    <tr>
                        <th>Severity</th>
                        <th>Category</th>
                        <th>Description</th>
                        <th>Mitigation</th>
                    </tr>
                </thead>
                <tbody>
                    {rows_html}
                </tbody>
            </table>
        </section>
"""


def _generate_map_hints_section(gdd: GameDesignDocument) -> str:
    """Generate the map hints section if present."""
    if not gdd.map_hints:
        return ""

    hints = gdd.map_hints
    biomes = ", ".join(b.value.replace("_", " ").title() for b in hints.biomes)

    # Special features
    features_html = ""
    if hints.special_features:
        feature_cards = []
        for feature in hints.special_features:
            reqs = ", ".join(feature.requirements) if feature.requirements else "None"
            feature_cards.append(f"""
                    <div class="card">
                        <h4>{_escape(feature.name)}</h4>
                        <p>Frequency: {_escape(feature.frequency)}</p>
                        <p style="margin: 10px 0">{_escape(feature.description)}</p>
                        <p style="color: var(--text-secondary)">Requirements: {_escape(reqs)}</p>
                    </div>""")
        features_html = f"""
            <h3>Special Features</h3>
            <div class="card-grid">
                {"".join(feature_cards)}
            </div>
"""

    return f"""
        <!-- Map Hints Section -->
        <section id="map-hints">
            <h2><span class="icon">Map Generation Hints</span></h2>
            
            <div class="card-grid">
                <div class="card">
                    <h4>Biomes</h4>
                    <p><strong>{_escape(biomes)}</strong></p>
                </div>
                <div class="card">
                    <h4>Map Size</h4>
                    <p style="font-size: 1.5rem; font-weight: bold; color: var(--neon-blue)">{_escape(hints.map_size)}</p>
                </div>
                <div class="card">
                    <h4>Connectivity</h4>
                    <p style="font-size: 1.5rem; font-weight: bold">{_escape(hints.connectivity)}</p>
                </div>
                <div class="card">
                    <h4>Generation Style</h4>
                    <p style="font-size: 1.5rem; font-weight: bold">{_escape(hints.generation_style)}</p>
                </div>
            </div>
            
            <h3>/Map Command</h3>
            <div class="card" style="background: var(--bg-primary); font-family: monospace;">
                <code style="color: var(--neon-green)">/Map {_escape(hints.to_map_command_args())}</code>
            </div>
            {features_html}
        </section>
"""


def _generate_footer(gdd: GameDesignDocument) -> str:
    """Generate the footer section."""
    return f"""
    <!-- Footer -->
    <footer>
        <p><strong>{_escape(gdd.meta.title)}</strong> - Game Design Document v{_escape(gdd.schema_version)}</p>
        <p>Generated by Game Planner - Dual-Agent Actor-Critic System</p>
        <p style="margin-top: 20px">{_escape(gdd.generated_at)}</p>
    </footer>
"""


def gdd_to_html(gdd: GameDesignDocument) -> str:
    """
    Convert a GameDesignDocument to a beautifully styled HTML document.

    The generated HTML includes:
    - Hero section with game title and badges
    - Sticky navigation bar
    - Meta info cards (genres, platforms, audience, dev time)
    - Core loop diagram with actions
    - Systems tables and cards
    - Progression timeline with milestones
    - Narrative section with story and themes
    - Character cards
    - Technical specifications with performance targets
    - Risk assessment table
    - Map generation hints (if present)

    The styling uses a dark theme with neon accents for a modern game design aesthetic.
    All CSS is embedded for single-file distribution.

    Args:
        gdd: The GameDesignDocument to convert

    Returns:
        Complete HTML document as a string
    """
    title = _escape(gdd.meta.title)
    css = _generate_css()

    # Generate all sections
    hero = _generate_hero_section(gdd)
    nav = _generate_navigation()
    meta = _generate_meta_section(gdd)
    core_loop = _generate_core_loop_section(gdd)
    systems = _generate_systems_section(gdd)
    progression = _generate_progression_section(gdd)
    narrative = _generate_narrative_section(gdd)
    characters = _generate_characters_section(gdd)
    technical = _generate_technical_section(gdd)
    risks = _generate_risks_section(gdd)
    map_hints = _generate_map_hints_section(gdd)
    footer = _generate_footer(gdd)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - Game Design Document</title>
    <style>
        {css}
    </style>
</head>
<body>
    {hero}
    {nav}
    <!-- Main Content -->
    <main class="container">
        {meta}
        {core_loop}
        {systems}
        {progression}
        {narrative}
        {characters}
        {technical}
        {risks}
        {map_hints}
    </main>
    {footer}
</body>
</html>
"""
