import obspython as obs

# --- ユーザー情報（最大8名） ---
user_data = [{"id": "", "url": "", "source": ""} for _ in range(20)]
use_test_discord_id = False
test_discord_id = ""

# --- 説明文（上部に表示される） ---
def script_description():
    return (
        "🎙️ **DiscordアイコンのCSS自動切り替えスクリプト**\n"
        "このスクリプトでは、最大8人分のDiscordユーザーごとに：\n"
        "・ユーザーのDiscord ID\n"
        "・表示する立ち絵画像のURL\n"
        "・対象となるOBSのブラウザソース名\n"
        "を設定し、OBS内でCSSを自動で適用できます。\n\n"
        "📌 各ブラウザソースには1人分の立ち絵のみ表示されるように構成されています。\n"
        "🔧 表示対象は発話時に明るくなり、他ユーザーは自動非表示になります。"
    )

# --- スクリプトUI定義 ---
def script_properties():
    props = obs.obs_properties_create()

    obs.obs_properties_add_bool(props, "use_test_discord_id", "テスト用Discord IDを使用する")
    obs.obs_properties_add_text(props, "test_discord_id", "テスト用Discord ID", obs.OBS_TEXT_DEFAULT)

    for i in range(20):
        obs.obs_properties_add_text(props, f"user_id_{i}", f"ユーザー{i+1} Discord ID", obs.OBS_TEXT_DEFAULT)
        obs.obs_properties_add_text(props, f"user_url_{i}", f"ユーザー{i+1} 画像URL", obs.OBS_TEXT_DEFAULT)
        obs.obs_properties_add_text(props, f"source_name_{i}", f"ユーザー{i+1} ブラウザソース名", obs.OBS_TEXT_DEFAULT)

    return props

# --- 設定変更時に呼ばれる処理 ---
def script_update(settings):
    global user_data, use_test_discord_id, test_discord_id

    use_test_discord_id = obs.obs_data_get_bool(settings, "use_test_discord_id")
    test_discord_id = obs.obs_data_get_string(settings, "test_discord_id").strip()

    for i in range(20):
        user_data[i]["id"] = obs.obs_data_get_string(settings, f"user_id_{i}").strip()
        user_data[i]["url"] = obs.obs_data_get_string(settings, f"user_url_{i}").strip()
        user_data[i]["source"] = obs.obs_data_get_string(settings, f"source_name_{i}").strip()

    update_all_sources()

# --- 全ブラウザソースにCSSを適用 ---
def update_all_sources():
    for user in user_data:
        source_name = user["source"]
        if not source_name:
            continue

        source = obs.obs_get_source_by_name(source_name)
        if source is None:
            continue

        settings = obs.obs_source_get_settings(source)
        if use_test_discord_id:
            discord_id = test_discord_id
        else:
            discord_id = user["id"]
        obs.obs_data_set_string(settings, "css", build_css(discord_id, user["url"]))
        obs.obs_source_update(source, settings)

        obs.obs_data_release(settings)
        obs.obs_source_release(source)

# --- 各ユーザー専用のCSS生成 ---
def build_css(discord_id, image_url):
    if not discord_id or not image_url:
        return ""

    css = f"""
img:not([src*="{discord_id}"]) {{
    display: none;
}}
img:not([src*="{discord_id}"]) + div {{
    display: none;
}}
img[src*="{discord_id}"] {{
    content: url("{image_url}");
    height: auto !important;
    width: 100% !important;
    border-radius: 0 !important;
    position: absolute;
    left: 50%;
    transform: translateX(-50%);
    filter: brightness(50%);
}}
img[src*="{discord_id}"].Voice_avatarSpeaking {{
    filter: brightness(100%);
}}
/* 発話状態の設定 */
img[class*="Voice_avatarSpeaking"] {{
    border-color: rgba(0,0,0,0) !important;
    filter: brightness(100%);
}}
div[class*='Voice_user'] {{
    display: none;
}}
body {{
    background-color: rgba(0, 0, 0, 0);
    overflow: hidden;
}}
"""
    return css
