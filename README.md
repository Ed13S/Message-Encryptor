# [Message-Encryptor](https://message-encryptor-yvo6.onrender.com)
# 📟 OTP STATION V12

### **🛑 CRITICAL RULE: THE ONE-TIME PAD PRINCIPLE**
This system follows strict **One-Time Pad (OTP)** logic. A pad is a unique key. Once a pad is used to **Decrypt**, it is "Burned" (moved to the vault) and should **never be used again**. Re-using a pad makes the encryption breakable.

---

### **🛠️ STEP 1: SYSTEM INITIALIZATION**
Before you can encrypt anything, you need a secret key (The Pad).
1. Navigate to the **[ ACTIVE PADS ]** section.
2. Click **`GENERATE MANUAL PAD`**.
3. **Result:** A new file (e.g., `otp0.txt`) will appear. This file contains 1,000 random shift values.

---

### **🔐 STEP 2: ENCRYPTING A MESSAGE**
*Use this when you want to turn a secret message into scrambled code.*

1. **Select Pad:** Click the filename (e.g., `otp0.txt`) in the active list. It will auto-fill the **Pad Filename** box.
2. **Input Text:** Type your secret message into the **Message Content** area.
3. **Execute:** Click the green **`ENCRYPT`** button.
4. **Action:** Copy the resulting scrambled text. You can now send this cipher to your recipient. 
   > **Note:** The pad remains "Active" until you choose to burn it.

---

### **🔥 STEP 3: DECRYPTING & BURNING**
*Use this to read a scrambled message. This action destroys the key.*

1. **Input Cipher:** Paste the scrambled text into the **Message Content** area.
2. **Identify Pad:** Ensure the **Pad Filename** matches the one used to encrypt the message.
3. **Execute:** Click the red **`DECRYPT & BURN`** button.
4. **Result:** The original message is revealed.
5. **The Burn:** The system automatically moves the pad to the **Burned Vault**. It is removed from the active list to ensure maximum security.

---

### **🔑 STEP 4: MASTER AUTHENTICATION (ADMIN)**
*Access the restricted "Red Zone" at the bottom of the interface.*

* **View Burned:** Enter your **Master Password** and click **`VIEW BURNED`**. This displays your history of used keys.
* **Restore:** If a pad was burned by mistake, click **`RESTORE`** to move it back to the active list.
* **Nuclear Purge:** Click **`NUCLEAR PURGE`** with the password entered to **permanently wipe** every file on the server.

---

### **📤 STEP 5: BACKUP & UPLOADS**
**IMPORTANT:** Because Render uses ephemeral storage, files are wiped when the server sleeps.
* **Download (DL):** Click **`DL`** next to any active pad to save it to your device.
* **Upload:** If your server resets, use the **`UPLOAD PAD`** tool to put your saved `.txt` keys back onto the station.
