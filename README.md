# [Message-Encryptor](https://message-encryptor-yvo6.onrender.com)
1. Initialization
When you first open your URL (e.g., https://your-app-name.onrender.com), the system performs a handshake with the server.

Check the Status: Look at the STATUS bar. It should read SYSTEM ONLINE.

Active Pads: If the list says EMPTY, click the GENERATE MANUAL PAD button. You will see otp0.txt appear in the list.

2. Encrypting a Message
Encryption turns your plain text into scrambled code that can only be read with your specific pad.

Select a Pad: Click on the name of a pad in the ACTIVE PADS list (e.g., otp0.txt). This will automatically fill the "Pad Filename" box.

Enter Content: Type your secret message into the large text area.

Execute: Click the green ENCRYPT button.

Result: The text in the box will change into scrambled characters. Copy this text and send it to your recipient.

3. Decrypting & Burning
Decryption reverses the process and immediately destroys the key to ensure it can never be used again.

Input Cipher: Paste the scrambled text you received into the text area.

Target Pad: Type in the exact name of the pad used to encrypt it.

Execute: Click the red DECRYPT & BURN button.

Verification: The message will return to plain text, and the pad (otp0.txt) will vanish from the active list and move to the "Burned" vault.

4. Vault Management (Admin Only)
The red area at the bottom is for high-level file management.

Viewing Burned Pads: Type "admin" into the Master Password box and click VIEW BURNED. A list of used pads will appear.

Restoration: If you accidentally burned a pad, click RESTORE next to the filename in the burned list to move it back to the active section.

Nuclear Purge: Clicking this with the correct password will delete every pad on the server permanently.

5. Moving Files (Upload/Download)
Download: Click the DL link next to any active pad. This saves the .txt file to your phone or computer. This is vital for backup since Render's free tier resets files occasionally.

Upload: If you have an OTP file from another device, click Choose File, select your .txt pad, and click UPLOAD PAD.
