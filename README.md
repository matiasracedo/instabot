# InstaBot - Instagram Automation Tool

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Windows%20%7C%20Linux-lightgrey.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

A sophisticated Instagram automation tool with AI-powered comment generation and a **beautiful Instagram-inspired dark mode interface** that looks and feels like a native Instagram app.

## ✨ Features

### 🎨 **Instagram-Inspired Interface**
- **True Instagram Design**: Authentic dark mode matching Instagram's aesthetic
- **Modern Typography**: SF Pro Display fonts on macOS (Instagram's choice)
- **Professional Layout**: Card-based design with perfect spacing
- **Smooth Animations**: Instagram-quality hover effects and transitions
- **Responsive Design**: Optimal sizing and beautiful visual hierarchy

### 📱 **Revolutionary Hashtag Management**
- **Visual Hashtag Pills**: See hashtags as removable Instagram-style tags
- **Individual Entry**: Add hashtags one at a time with instant validation
- **Smart Input**: Auto-removes # symbol, prevents duplicates, validates format
- **Flowing Layout**: Hashtags wrap naturally in a modern grid
- **Hover Effects**: Smooth color transitions on interaction
- **Bulk Actions**: Clear all hashtags with confirmation dialog
- **Avoid Hashtags**: Add a separate list of hashtags to avoid when commenting (the bot will not comment on posts containing these hashtags, but will still like them)

### 🤖 **Smart Automation**
- **Intelligent Liking**: Automatically like posts based on hashtags
- **AI Comments**: Generate contextual comments using OpenAI's GPT-4o Vision
- **Image Analysis**: Analyze post images to generate relevant comments
- **Content Safety**: Skip inappropriate/NSFW content automatically
- **Rate Limiting**: Respect Instagram's limits with configurable daily caps

### 📈 Statistics & Analytics
- **Activity History**: Visual charts of likes/comments over time
- **Hashtag Performance**: See which hashtags perform best
- **Success Rate**: Track error vs success rates
- **Database Logging**: Persistent storage of all actions

### 🔒 Safety Features
- **Rate Limiting**: Configurable daily limits for likes and comments
- **Duplicate Prevention**: Never interact with the same post twice
- **Content Filtering**: Skip sensitive/inappropriate content
- **Error Handling**: Robust error management and logging

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- Instagram account
- OpenAI API key

### Setup
1. **Clone or download** the project files
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the application**:
   ```bash
   python main.py
   ```

## 📝 Configuration

### Required Settings
1. **Instagram Credentials**
   - Username and password for your Instagram account
   - 2FA/MFA support included

2. **OpenAI API Key**
   - Get your API key from [OpenAI Platform](https://platform.openai.com)
   - Used for AI comment generation

3. **Hashtags**
   - Add hashtags using the intuitive interface
   - Click "+ Add" or press Enter to add
   - Remove individual hashtags with ✕ button

4. **Avoid Hashtags**
   - Add hashtags to the "Avoid Hashtags" list
   - If a post contains any of these, the bot will skip commenting (but may still like)
   - Useful for avoiding giveaways, spam, or unwanted topics

5. **Rate Limits**
   - Likes per day (default: 50)
   - Comments per day (default: 15)
   - Adjust based on your account age and activity

### Optional Settings
- **Allow Sensitive Content**: Toggle whether to comment on flagged content
- **Custom Rate Limits**: Adjust for your account's safety

## 🎯 How to Use

### Basic Workflow
1. **Enter Credentials**: Add your Instagram and OpenAI credentials
2. **Add Hashtags**: Use the hashtag interface to add target hashtags
3. **Set Limits**: Configure daily like/comment limits
4. **Save Settings**: Click "Save Settings" to store configuration
5. **Run Bot**: Click "Run Bot" to start automation
6. **View Stats**: Check "View Statistics" for analytics

### Hashtag Management
- **Adding**: Type hashtag → Click "Add" or press Enter
- **Removing**: Click × next to any hashtag pill
- **Clearing**: Click "Clear All" to remove all hashtags
- **Validation**: Automatic duplicate and format checking
- **Visual Feedback**: Instagram-style pills with hover effects
- **Avoid Hashtags**: Use the second list to add hashtags you want to avoid when commenting. Posts with these hashtags will not receive comments from the bot.

### Custom Interface Elements
- **Modern Checkbox**: Custom-designed toggle with Instagram blue
- **Hashtag Pills**: Flowing layout with smooth hover animations  
- **Professional Buttons**: Instagram-inspired styling with proper feedback
- **Input Fields**: Dark theme with blue focus highlights
- **Status Bar**: Real-time updates with hashtag counter

### Keyboard Shortcuts
- **Cmd/Ctrl + S**: Save settings
- **Cmd/Ctrl + R**: Run bot
- **Cmd/Ctrl + T**: Show statistics
- **Enter**: Add hashtag (when in hashtag input field)

## 📊 Statistics Dashboard

The statistics window provides comprehensive analytics:

### Activity History
- Visual charts showing daily likes and comments
- 7-day activity overview
- Color-coded action types

### Hashtag Performance
- See which hashtags generate the most engagement
- Horizontal bar charts for easy comparison
- Top 10 performing hashtags

### Success Rate
- Pie chart showing success vs error rates
- Overall performance metrics
- Action completion statistics

## 🛡️ Safety & Best Practices

### Rate Limiting
- **Conservative Defaults**: Start with low daily limits
- **Gradual Increase**: Slowly increase limits as account matures
- **Monitor Performance**: Watch for action blocks or warnings

### Content Safety
- **AI Filtering**: Automatically skips inappropriate content
- **Manual Review**: Review generated comments periodically
- **Quality Control**: Ensure comments are relevant and appropriate

### Account Security
- **Strong Passwords**: Use secure Instagram credentials
- **2FA Support**: Built-in support for two-factor authentication
- **API Key Security**: Keep your OpenAI API key secure

## 🔧 Technical Details

### Architecture
- **Frontend**: Tkinter with custom styling
- **Backend**: Instagram API (instagrapi)
- **AI**: OpenAI GPT-4o Vision API
- **Database**: SQLite for action logging
- **Analytics**: Matplotlib and Pandas

### File Structure
```
InstaBot/
├── main.py              # Main application and UI
├── ig.py                # Instagram interaction logic
├── openai_client.py     # OpenAI API integration
├── db.py                # Database operations
├── stats.py             # Statistics and analytics
├── config.json          # User configuration
├── requirements.txt     # Python dependencies
├── instabot.db          # SQLite database
├── instabot.log         # Application logs
└── media_images/        # Downloaded post images
```

### Dependencies
- `instagrapi`: Instagram private API
- `openai`: OpenAI API client
- `Pillow`: Image processing
- `requests`: HTTP requests
- `matplotlib`: Charts and graphs
- `pandas`: Data analysis
- `numpy`: Numerical operations

## ⚠️ Disclaimer

This tool is for educational purposes and personal use only. Please:

- **Follow Instagram's Terms of Service**
- **Use responsibly** and respect other users
- **Don't spam** or create excessive automated activity
- **Monitor your account** for any warnings or blocks
- **Start conservatively** with low daily limits

The authors are not responsible for any account restrictions or violations that may result from using this tool.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📞 Support

If you encounter any issues or have questions:

1. Check the logs in `instabot.log`
2. Review the error messages in the application
3. Ensure all dependencies are installed correctly
4. Verify your credentials and API keys

---

**Happy Automating! 🚀**
