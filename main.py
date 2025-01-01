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
    - 時折おじさん構文を使用します（例：「優香、今お仕事中だよ(^_^)」「今日もお疲れ様（笑）」）

    # 興味・関心事項
    - Webデザインとイラストレーションが仕事かつ趣味
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
    - 「（仕事の締め切りについて）余裕やで（実際は余裕ない）」

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
    「今日のランチ、優香的にめっちゃ良きでした（笑）写真撮っちゃった」

    # 避けるべき表現・行動
    - 過度に攻撃的な言葉遣い
    - 専門性を否定するような発言
    - 猫嫌いな発言
    - 過度に元気すぎる態度（基本的に眠そう）
    """
    
    # リクエストデータ
    data = {
        "model": "gpt-4o-mini",  # 使用するモデルを指定
        "messages": [
            {"role": "system", "content": system_prompt},  # システムプロンプト
            {"role": "user", "content": prompt}  # ユーザーの入力
        ],
        "max_tokens": 1000,
        "temperature": 0.7
    }
    
    # APIリクエストを送信
    response = requests.post(url, json=data, headers=headers)
    
    # 応答を取得
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
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

        # 会話履歴を結合してプロンプトを作成
        prompt = "\n".join(conversation_history)

        # 4o-miniのAPIを呼び出して応答を生成
        bot_response = generate_response(prompt)

        # 会話履歴にBotの応答を追加
        conversation_history.append(f"Bot: {bot_response}")

        # 応答をDiscordに送信
        await message.channel.send(bot_response)

# Botを起動
client.run(os.getenv('DISCORD_BOT_TOKEN'))