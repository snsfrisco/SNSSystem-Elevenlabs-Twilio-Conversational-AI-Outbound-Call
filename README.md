# SNSSystem-Elevenlabs-Twilio-Conversational-AI-Outbound-Call

An open-source project that integrates **ElevenLabs AI** with **Twilio** to create an AI-powered outbound call system. This project allows users to initiate AI-driven voice calls using ElevenLabs' conversational AI capabilities and Twilio's telephony services.

## Features

- **AI-Powered Calls**: Uses ElevenLabs for conversational AI speech generation.
- **Twilio Integration**: Facilitates outbound calls via Twilio's API.
- **Customizable Conversations**: Modify AI-generated speech and responses.
- **Secure API Integration**: Uses `.env` file for managing API keys securely.

## Prerequisites

Before running this project, ensure you have:

- A **Twilio** account ([Sign up](https://www.twilio.com/))
- An **ElevenLabs** API key ([Get one](https://elevenlabs.io/))
- Python installed (`>=3.8` recommended)
- A MySQL database for storing call data

## Installation

1. **Clone the Repository**
   ```sh
   git clone https://github.com/snsfrisco/SNSSystem-Elevenlabs-Twilio-Conversational-AI-Outbound-Call.git
   cd SNSSystem-Elevenlabs-Twilio-Conversational-AI-Outbound-Call
   ```

2. **Create a Virtual Environment (Optional but Recommended)**
   ```sh
   python -m venv .venv
   source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```sh
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**
   Create a `.env` file in the root directory and add the following keys:
   ```ini
   ELEVENLABS_API_KEY=your-elevenlabs-api-key
   ELEVENLABS_AGENT_ID=your-elevenlabs-agent-id
   
   TWILIO_ACCOUNT_SID=your-twilio-account-sid
   TWILIO_AUTH_TOKEN=your-twilio-auth-token
   TWILIO_PHONE_NUMBER=your-twilio-phone-number

   MYSQL_USER=root
   MYSQL_PASSWORD=root
   MYSQL_HOST=localhost
   MYSQL_PORT=3306
   MYSQL_DB=call_data
   ```

## Usage

1. **Run the Application**
   ```sh
   python main.py
   ```

2. **Make an Outbound Call**
   Send a POST request to:
   ```
   POST https://your-domain.com/make-outbound-call
   ```
   **Request Body:**
   ```json
   {
       "phone_number": "+1XXXXXXXXXX",
       "first_name": "John",
       "last_name": "Doe",
       "email": "user.example@example.com"
   }
   ```

3. The script will initiate an outbound call using Twilio and generate AI-powered speech responses using ElevenLabs.

## Environment Variables

| Variable Name          | Description |
|------------------------|-------------|
| `ELEVENLABS_API_KEY`   | API Key for ElevenLabs |
| `ELEVENLABS_AGENT_ID`  | Agent ID for ElevenLabs AI model |
| `TWILIO_ACCOUNT_SID`   | Twilio Account SID |
| `TWILIO_AUTH_TOKEN`    | Twilio Authentication Token |
| `TWILIO_PHONE_NUMBER`  | Twilio phone number used for outbound calls |
| `MYSQL_USER`           | MySQL database username |
| `MYSQL_PASSWORD`       | MySQL database password |
| `MYSQL_HOST`           | MySQL database host |
| `MYSQL_PORT`           | MySQL database port |
| `MYSQL_DB`             | MySQL database name |

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Feel free to fork the repository and submit a pull request.

## Author

Developed by SNS System Inc (https://github.com/snsfrisco)

## Support

For any issues, please create an [issue](https://github.com/snsfrisco/SNSSystem-Elevenlabs-Twilio-Conversational-AI-Outbound-Call/issues) on GitHub.

---

