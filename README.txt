Требования 
python3.12
linux

После клонирования репозиторий необходимо вручную поместить файл .env, содержащий токен бота

git clone https://github.com/Olga-Latunova/VK-Teams-BOT.git
cd VK-Teams-BOT/
python3 -m venv VKbot
source VKbot/bin/activate
pip install -r requirements.txt
python3 main.py