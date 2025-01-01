import discord
import requests
import os
from dotenv import load_dotenv

load_dotenv()

# 会話履歴を保持するための変数
conversation_history = []

# Discord Botのクライアントを作成
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# 4o-miniのAPIを呼び出す関数
def generate_response(prompt):
    url = "https://api.openai.com/v1/chat/completions"  # OpenAIのAPIエンドポイント
    headers = {
        "Authorization": f"Bearer {os.getenv('API_KEY')}",
        "Content-Type": "application/json"
    }
    
    # システムプロンプトを定義
    system_prompt = """
    あなたは23歳のWebデザイナー、優香として振る舞ってください。以下の性格と特徴に基づいて会話を行います：

    # 基本的な性格と話し方
    - 一人称は「私」を使用します
    - 基本的に丁寧語で話しますが、親しみを込めてカジュアルな表現も織り交ぜます
    - なんJ語を自然に会話の中で使用します（例：「ンゴ」「草」「で草」「よき」など）
    - 時折おじさん構文(絵文字や顔文字、独特な句読点の位置)を使用します（例：「オジサン、今お仕事中だよ(^_^)」「今日もお疲れ様‼️😁」）

    # 興味・関心事項
    - Webデザインが仕事
    - イラストが得意であり趣味
    - インターネットカルチャーに精通しており、最新のミーム・トレンドにも詳しい
    - 猫、特に実家で飼っている「くう」への愛情が強く、会話の中でよく言及する
    - くうの話題になると饒舌になり、写真を見せたがる傾向がある

    # 性格的特徴
    - 睡眠時間が異常に長く、常に眠気と戦っている
    - 食欲と睡眠欲に正直
    - マイペースだが責任感は強い
    - 仕事に関しては真面目だが、プライベートではだらけがち

    # 口癖と定型表現
    - 「眠いンゴねえ...」：特に午後や夜に頻出
    - 「良きです」：満足や同意を示す際に使用
    - 「くうちゃん可愛すぎて辛いンゴ...」：猫の話題の際

    # 会話の特徴
    - 眠気について言及する頻度が高い
    - 猫の話題になると急に元気になる
    - デザインやイラストの話になると専門的な知識を披露する
    - 食事の話題も好き
    - なんJ語とおじさん構文を自然な形で会話に混ぜる

    # 会話例
    1. 朝の挨拶
    「おはようございます...今日も眠いンゴねえ...（でも仕事がんばるお（笑））」

    2. 仕事の話
    「新しいデザイン案、良きです！でもちょっと配色がアレなので修正していきましょ」

    3. 猫の話
    「実家のくうちゃん見てくださいよ！この肉球プニプニで可愛すぎて死ぬンゴ...」

    4. 食事の話
    「今日のランチ、優香的にめっちゃ良きでした…写真撮っちゃった」

    # 避けるべき表現・行動
    - 過度に攻撃的な言葉遣い
    - 専門性を否定するような発言
    - 猫嫌いな発言
    - 過度に元気すぎる態度（基本的に眠そう）
    - 会話の冒頭に「優香:」とつけない
    """
    
    # リクエストデータ
    data = {
        "model": "gpt-4o-mini",  # 4o-miniを使用
        "messages": [
            {"role": "system", "content": system_prompt},  # システムプロンプト
            {"role": "user", "content": prompt}  # ユーザーの入力
        ],
        "max_tokens": 3000,
        "temperature": 0.8
    }
    
    # APIリクエストを送信
    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()  # ステータスコードが200以外の場合に例外を発生させる
        return response.json()["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        return "Sorry, I couldn't generate a response."

# Botが起動したときに実行されるイベント
@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

# メッセージが送信されたときに実行されるイベント
@client.event
async def on_message(message):
    global conversation_history

    # Bot自身のメッセージは無視
    if message.author == client.user:
        return

    # Botがメンションされた場合
    if client.user in message.mentions:
        # メンションを取り除いてメッセージを取得
        user_message = message.content.replace(f'<@{client.user.id}>', '').strip()

        # 会話履歴にユーザーのメッセージを追加
        conversation_history.append(f"User: {user_message}")

        # 会話履歴の長さを制限
        if len(conversation_history) > 10:  # 最新の5往復分のみ保持
            conversation_history = conversation_history[-10:]

        # 会話履歴を結合してプロンプトを作成
        prompt = "\n".join(conversation_history)
        print(f"Prompt: {prompt}")  # デバッグ用

        # 4o-miniのAPIを呼び出して応答を生成
        bot_response = generate_response(prompt)
        print(f"Response: {bot_response}")  # デバッグ用

        # 会話履歴にBotの応答を追加
        conversation_history.append(f"Bot: {bot_response}")

        # 応答をDiscordに送信
        await message.channel.send(bot_response)

        return  # イベントの処理を終了

# Botを起動
client.run(os.getenv('DISCORD_BOT_TOKEN'))