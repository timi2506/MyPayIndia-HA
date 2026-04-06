# MyPayIndia-HA
A simple HomeAssistant Integration for MyPayIndia
<img width="1457" height="1056" alt="Screenshot 2026-04-06 at 11 19 58" src="https://github.com/user-attachments/assets/0b41eb1f-95ff-48cf-9695-6a60deca4ff4" />


## Installation
### Via HACS (easiest)
Follow the instructions in the Video

https://github.com/user-attachments/assets/a129cbe5-f713-4c8b-9058-2468a2e3e64a

Text based Instructions: 
- Go to the HACS Tab
- Press the Three Dots in the Top Right Corner -> Custom repositories
- Type "https://github.com/timi2506/MyPayIndia-HA" as repository and select "Integration" as Type, then press "Add"
- Once you've added it, you can install it by searching for "MyPayIndia" in the search bar at the top, pressing on it and hitting "Download"
### Install Script (advanced)
Open the Terminal or connect to your HomeAssistant via SSH and execute:
```bash
curl -sSL https://raw.githubusercontent.com/timi2506/MyPayIndia-HA/main/install.sh | bash
```
## Configuration

After installing this custom component you can add the cards for MyPayIndia by 
1. Going to: `YOUR_HOMEASSISTANT_BASE_URL/config/lovelace/resources`
2. Pressing "Add Resource" and entering: `/mypayindia_static/mypayindia-card.js` + selecting "JavaScript module"
3. Adding the Cards to one of your Dashboard's

> [!TIP]
> If you face issues with cards not changing after an update, you can either
> a) Clear your Browser Caches and refresh OR
> b) Add ?v=randomNumber after /mypayindia_static/mypayindia-card.js, as long as the randomNumber is different from previous numbers (if you did this before)
