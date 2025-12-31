"""
quick_generate.py - YAML 템플릿에서 GDD 빠르게 생성

사용법:
    python quick_generate.py my_game.yaml
    python quick_generate.py my_game.yaml --output my_game.html
"""

import sys
import yaml
from pathlib import Path
from datetime import datetime, timezone

from models import (
    GameDesignDocument,
    GameMeta,
    CoreLoop,
    GameSystem,
    Progression,
    Narrative,
    TechnicalSpec,
    Risk,
    Character,
    SystemParameter,
    Milestone,
    AudioRequirements,
    Genre,
    Platform,
    ProgressionType,
    ArtStyle,
    SystemType,
    GameEngine,
    Severity,
    NarrativeDelivery,
)
from html_template import gdd_to_html


def load_yaml_template(file_path: str) -> dict | None:
    """YAML 템플릿 파일 로드

    Returns:
        dict: 파싱된 YAML 데이터
        None: 로드 실패 시
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            if data is None:
                print(f"❌ 오류: YAML 파일이 비어있습니다: {file_path}")
                return None
            if not isinstance(data, dict):
                print(
                    f"❌ 오류: YAML 파일은 딕셔너리 형태여야 합니다. 현재 타입: {type(data).__name__}"
                )
                return None
            return data
    except FileNotFoundError:
        print(f"❌ 오류: 파일을 찾을 수 없습니다: {file_path}")
        return None
    except yaml.YAMLError as e:
        print(f"❌ 오류: YAML 파싱 실패")
        print(f"   원인: {e}")
        # yaml.MarkedYAMLError has problem_mark attribute
        mark = getattr(e, "problem_mark", None)
        if mark is not None:
            print(f"   위치: 라인 {mark.line + 1}, 컬럼 {mark.column + 1}")
        return None
    except PermissionError:
        print(f"❌ 오류: 파일 읽기 권한이 없습니다: {file_path}")
        return None
    except Exception as e:
        print(f"❌ 오류: 파일 로드 중 예상치 못한 오류 발생")
        print(f"   원인: {type(e).__name__}: {e}")
        return None


def create_gdd_from_template(data: dict) -> GameDesignDocument | None:
    """템플릿 데이터에서 GDD 생성

    Returns:
        GameDesignDocument: 생성된 GDD
        None: 생성 실패 시
    """
    try:
        return _create_gdd_from_template_impl(data)
    except KeyError as e:
        print(f"❌ 오류: 필수 필드가 누락되었습니다: {e}")
        return None
    except TypeError as e:
        print(f"❌ 오류: 데이터 타입이 올바르지 않습니다")
        print(f"   원인: {e}")
        return None
    except ValueError as e:
        print(f"❌ 오류: 잘못된 값이 포함되어 있습니다")
        print(f"   원인: {e}")
        return None
    except Exception as e:
        print(f"❌ 오류: GDD 생성 중 예상치 못한 오류 발생")
        print(f"   원인: {type(e).__name__}: {e}")
        return None


def _create_gdd_from_template_impl(data: dict) -> GameDesignDocument:
    """템플릿 데이터에서 GDD 생성 (내부 구현)"""

    # 1. 장르 파싱
    genres = []
    for g in data.get("genre", ["puzzle"]):
        try:
            genres.append(Genre(g))
        except ValueError:
            genres.append(Genre.PUZZLE)

    # 2. 플랫폼 파싱
    platforms = []
    for p in data.get("platforms", ["pc"]):
        try:
            platforms.append(Platform(p))
        except ValueError:
            platforms.append(Platform.PC)

    # 3. Meta 정보
    meta = GameMeta(
        title=data.get("title", "Untitled Game"),
        genres=genres,
        target_platforms=platforms,
        target_audience=data.get("target_audience", "전체 이용가를 위한 캐주얼 게이머"),
        unique_selling_point=data.get(
            "core_concept", "독특한 게임 경험을 제공하는 혁신적인 메카닉"
        ),
        elevator_pitch=data.get("core_mechanic", ""),
        estimated_dev_time_weeks=data.get("dev_weeks", 52),
    )

    # 4. Core Loop
    loop_actions = data.get("core_loop", ["시작", "플레이", "종료"])
    core_mechanic = data.get("core_mechanic", "도전적인 게임플레이")
    core_loop = CoreLoop(
        primary_actions=loop_actions,
        challenge_description=core_mechanic
        if len(core_mechanic) >= 20
        else f"{core_mechanic} - 플레이어에게 도전적인 경험 제공",
        reward_description="성취감과 진행을 통한 보상 시스템으로 플레이어 동기 부여",
        loop_description=" -> ".join(loop_actions) + " -> 반복하며 성장",
        session_length_minutes=data.get("session_length", 15),
        hook_elements=["독특한 메카닉", "몰입감 있는 경험"],
    )

    # 5. 시스템 생성
    systems = []
    system_types = [
        SystemType.COMBAT,
        SystemType.MOVEMENT,
        SystemType.INVENTORY,
        SystemType.UI,
        SystemType.SAVE_LOAD,
    ]

    for i, sys_data in enumerate(data.get("systems", [])):
        if isinstance(sys_data, dict):
            name = sys_data.get("name", f"시스템 {i + 1}")
            desc = sys_data.get("description", "")
            priority_val = sys_data.get("priority", 5)
            if isinstance(priority_val, str):
                priority_map = {"high": 1, "medium": 5, "low": 8}
                priority_val = priority_map.get(priority_val.lower(), 5)
        else:
            name = str(sys_data)
            desc = ""
            priority_val = 5

        # Ensure description meets minimum length
        if len(desc) < 20:
            desc = f"{name}의 기본 설명 - 게임의 핵심 기능을 담당하는 시스템"

        system = GameSystem(
            name=name,
            description=desc,
            type=system_types[i % len(system_types)],
            priority=min(max(priority_val, 1), 10),  # Clamp to 1-10
            mechanics=[f"{name} 기본 메카닉"],
            parameters=[
                SystemParameter(
                    name="기본 설정",
                    type="float",
                    default_value="1.0",
                    description="기본 파라미터 설정값",
                )
            ],
            dependencies=[],
        )
        systems.append(system)

    # 시스템이 3개 미만이면 기본 시스템 추가 (최소 3개 필요)
    default_systems = [
        GameSystem(
            name="코어 게임플레이 시스템",
            description="게임의 핵심 게임플레이 로직을 담당하는 메인 시스템",
            type=SystemType.MOVEMENT,
            priority=1,
            mechanics=["기본 메카닉", "플레이어 입력 처리"],
            parameters=[],
            dependencies=[],
        ),
        GameSystem(
            name="UI 인터페이스 시스템",
            description="사용자 인터페이스와 HUD를 담당하는 시스템",
            type=SystemType.UI,
            priority=2,
            mechanics=["메뉴 시스템", "HUD 표시"],
            parameters=[],
            dependencies=[],
        ),
        GameSystem(
            name="저장 및 로드 시스템",
            description="게임 진행 상황의 저장과 로드를 담당하는 시스템",
            type=SystemType.SAVE_LOAD,
            priority=3,
            mechanics=["자동 저장", "수동 저장", "로드"],
            parameters=[],
            dependencies=[],
        ),
    ]

    while len(systems) < 3:
        systems.append(default_systems[len(systems)])

    # 6. Progression - 최소 5개의 마일스톤 필요
    milestones = [
        Milestone(
            name="Tutorial Complete",
            description="Learn basic controls and understand core mechanics of the game",
            unlock_condition="Complete the first stage of the tutorial",
            rewards=["Basic features unlocked"],
        ),
        Milestone(
            name="Chapter 1 Complete",
            description="Complete the first chapter of the story and enter the game world",
            unlock_condition="Defeat the Chapter 1 boss battle",
            rewards=["New ability unlocked"],
        ),
        Milestone(
            name="Midpoint Reached",
            description="Reach the midpoint of the game and experience core content",
            unlock_condition="Achieve 50% overall game progress",
            rewards=["Advanced features unlocked"],
        ),
        Milestone(
            name="Climax Entered",
            description="Enter the climax section of the game where challenges intensify",
            unlock_condition="Begin the final chapter of the story",
            rewards=["Ultimate equipment unlocked"],
        ),
        Milestone(
            name="Game Complete",
            description="Complete the main story and reach the ending of the game",
            unlock_condition="Clear the final stage and defeat the last boss",
            rewards=["Ending unlocked", "Bonus content unlocked"],
        ),
    ]

    progression = Progression(
        type=ProgressionType.LEVEL_BASED,
        difficulty_curve_description="초반에는 완만하게 시작하여 중반부터 점진적으로 어려워지며, 후반에는 숙련된 플레이어를 위한 도전적인 난이도 제공",
        milestones=milestones,
        unlocks=[],
    )

    # 7. Narrative
    story_data = data.get("story", {})
    themes = story_data.get("themes", ["모험", "성장"])

    characters = []
    for char_data in data.get("characters", []):
        if isinstance(char_data, dict):
            role_str = char_data.get("role", "Protagonist")
            char_desc = char_data.get("description", "캐릭터 설명")
            if len(char_desc) < 20:
                char_desc = (
                    f"{char_data.get('name', '캐릭터')}의 상세한 캐릭터 설명 및 배경"
                )

            character = Character(
                name=char_data.get("name", "캐릭터"),
                role=role_str,
                description=char_desc,
                motivation="목표 달성을 위한 여정",
                abilities=["기본 능력"],
            )
            characters.append(character)

    setting = story_data.get("setting", "게임 세계")
    if len(setting) < 10:
        setting = f"{setting} - 플레이어가 모험하게 될 독특한 세계관"

    story_premise = story_data.get("premise", "모험의 시작")
    if len(story_premise) < 20:
        story_premise = (
            f"{story_premise} - 플레이어는 새로운 여정을 시작하며 다양한 도전에 직면"
        )

    narrative = Narrative(
        setting=setting,
        story_premise=story_premise,
        themes=themes,
        characters=characters,
        narrative_delivery=[
            NarrativeDelivery.DIALOGUE,
            NarrativeDelivery.ENVIRONMENTAL,
        ],
        story_structure="선형적 스토리 구조로 시작, 전개, 클라이맥스, 결말의 흐름",
        key_story_beats=["시작", "전개", "클라이맥스", "결말"],
    )

    # 8. Technical
    art_style_str = data.get("art_style", "stylized")
    try:
        art_style = ArtStyle(art_style_str)
    except ValueError:
        art_style = ArtStyle.STYLIZED

    audio = AudioRequirements(
        music_style="게임 분위기에 맞는 배경음악과 효과음",
        sound_categories=["배경음악", "효과음", "UI 사운드"],
        voice_acting=False,
        adaptive_music=False,
    )

    technical = TechnicalSpec(
        recommended_engine=GameEngine.UNITY,
        art_style=art_style,
        key_technologies=["게임 엔진", "물리 시스템", "저장 시스템"],
        audio=audio,
        accessibility_features=["자막", "조작 설정"],
        networking_required=False,
    )

    # 9. Risks
    risks = [
        Risk(
            category="Technical",
            severity=Severity.MAJOR,
            description="기술적 도전 - 새로운 시스템 구현 시 예상치 못한 문제 발생 가능",
            mitigation="단계적 개발과 지속적인 테스트를 통한 리스크 최소화",
        ),
        Risk(
            category="Design",
            severity=Severity.MAJOR,
            description="밸런스 조정 필요 - 게임 난이도와 보상 시스템의 균형 필요",
            mitigation="반복적인 플레이테스트와 피드백 수집을 통한 개선",
        ),
    ]

    # 10. GDD 생성
    gdd = GameDesignDocument(
        meta=meta,
        core_loop=core_loop,
        systems=systems,
        progression=progression,
        narrative=narrative,
        technical=technical,
        risks=risks,
        generated_at=datetime.now(timezone.utc).isoformat(),
        schema_version="1.0",
    )

    return gdd


def main():
    if len(sys.argv) < 2:
        print("사용법: python quick_generate.py <template.yaml> [--output <file.html>]")
        print("\n예시:")
        print("  python quick_generate.py my_game.yaml")
        print("  python quick_generate.py my_game.yaml --output my_game.html")
        sys.exit(1)

    template_path = sys.argv[1]

    # Output 파일 처리
    output_path = None
    if "--output" in sys.argv:
        idx = sys.argv.index("--output")
        if idx + 1 < len(sys.argv):
            output_path = sys.argv[idx + 1]

    # 템플릿 로드
    print(f"📄 템플릿 로드: {template_path}")
    data = load_yaml_template(template_path)
    if data is None:
        print(
            "💡 팁: YAML 파일 형식을 확인하세요. 들여쓰기와 콜론(:) 사용에 주의하세요."
        )
        sys.exit(1)

    # GDD 생성
    print(f"🎮 GDD 생성 중...")
    gdd = create_gdd_from_template(data)
    if gdd is None:
        print("💡 팁: YAML 템플릿의 필수 필드와 데이터 형식을 확인하세요.")
        sys.exit(1)

    # HTML 변환
    print(f"🖥️ HTML 변환 중...")
    try:
        html = gdd_to_html(gdd)
    except Exception as e:
        print(f"❌ 오류: HTML 변환 실패")
        print(f"   원인: {type(e).__name__}: {e}")
        sys.exit(1)

    # 저장
    if not output_path:
        # 자동 파일명 생성
        title_slug = gdd.meta.title.lower().replace(" ", "-")
        output_path = f"gdd-{title_slug}.html"

    try:
        Path(output_path).write_text(html, encoding="utf-8")
        print(f"✅ 저장 완료: {output_path}")
    except PermissionError:
        print(f"❌ 오류: 파일 쓰기 권한이 없습니다: {output_path}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 오류: 파일 저장 실패")
        print(f"   원인: {type(e).__name__}: {e}")
        sys.exit(1)

    # 브라우저에서 열기
    import webbrowser

    try:
        webbrowser.open(Path(output_path).absolute().as_uri())
        print(f"🌐 브라우저에서 열기...")
    except Exception:
        # 브라우저 열기 실패는 치명적이지 않음
        print(
            f"⚠️ 브라우저를 자동으로 열 수 없습니다. 수동으로 열어주세요: {output_path}"
        )


if __name__ == "__main__":
    main()
