import os
import requests
from datetime import datetime

DISCORD_WEBHOOK = os.environ["WEBHOOK"]
release_url = "https://github.com/Oneloutre/kernel_auto_builder/releases/tag/latest"
codename = os.environ["DEVICE_CODENAME"]
kernel_version = os.environ["KERNEL_VERSION"]
zip_name = os.environ["NAME"]
embed_color = 0x2ecc71

embed = {
    "type": "rich",
    "username": "Kramel Slave",
    "embeds": [
        {
            "title": f"🚀 Build succeeded !",
            "url": release_url,
            "description": f"The KernelSU-Next build for **{codename}** is done !\n🎯 **Version :** `{kernel_version}`\n💡 **Name :** `{zip_name}`",
            "color": f"{embed_color}",
            "fields": [
                {
                    "name": "📥 Download",
                    "value": f"[Click here to go to the download page]({release_url})",
                    "inline": False
                },
                {
                    "name": "📅 Date",
                    "value": f"{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
                    "inline": True
                }
            ],
            "timestamp": datetime.now().isoformat(),
            "footer": {
                "text": "Automated build • GitHub Actions",
                "icon_url": "https://cdn-icons-png.flaticon.com/512/733/733609.png"
            }
        }
    ]
}

response = requests.post(DISCORD_WEBHOOK, json=embed)
if response.status_code == 204:
    print("✅ Notification sent on Discord !")
else:
    print(f"❌ Error ({response.status_code}) : {response.text}")