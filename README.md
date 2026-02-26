# 🕷️ Scrappers - The Data Harvesting Toolkit

> *"If data is the new oil, then these are your extraction rigs... except way less likely to cause environmental disasters."*

Welcome to **Scrappers**, the repository where data doesn't just grow on trees—we shake those trees until every last byte falls out! This is your one-stop shop for liberating data from the digital wilderness and bringing it home in nice, organized JSON files (or folders full of pretty pictures).

## 🎭 What's This All About?

Ever wanted to download an entire Instagram profile but manually saving images felt too much like actual work? Or maybe you needed to scrape a WordPress site but got lost in a maze of nested sitemaps? Yeah, me too. So I built these tools.

This repository contains a collection of web scraping utilities that do the boring stuff so you don't have to. Each tool is lovingly crafted with error handling, progress tracking, and enough resilience to survive the internet's mood swings.

## 🛠️ The Arsenal

### 1. 📸 [Instaloader](./Instaloader/) - The Instagram Image Hoarder

Because sometimes you need to archive someone's entire aesthetic™ for... research purposes.

**What it does:**
- Downloads all images from any Instagram profile (public or private, if you have access)
- Handles rate limiting like a champ (it'll wait patiently instead of throwing a tantrum)
- Supports multiple authentication methods (password, 2FA, session files, or just a sessionid cookie)
- Smart enough to only download new posts on subsequent runs (`--fast-update`)
- Saves metadata because context matters

**Quick Start:**
```bash
cd Instaloader
pip install instaloader
python main.py <instagram_username>
```

*Warning: Your hard drive may experience sudden growth spurts.*

### 2. 🌐 [WordPress Scraper](./wordpress/) - The Sitemap Excavator

For when you need to turn an entire website into a pile of neatly organized JSON files.

**What it does:**
- Recursively crawls through sitemap indexes (yes, it handles nested sitemaps!)
- Extracts titles, paragraphs, and special content sections
- Removes annoying stuff like cookie banners and footers
- Saves everything to JSON with proper UTF-8 encoding
- Shows progress so you know it's not stuck in an existential crisis
- Creates output directories automatically (because who has time for mkdir?)

**Quick Start:**
```bash
cd wordpress
pip install -r requirements.txt
python main.py  # Uses default settings (scrapes dspa.pt)
```

**Customize it:**
```python
from main import web_scraper_start

web_scraper_start(
    base_url='https://example.com/',
    sitemap_url='https://example.com/sitemap.xml',
    save_folder='my_data_treasure'
)
```

## 🚀 Installation

Each scraper lives in its own folder with its own README and dependencies. They're like independent adults but living under the same roof.

```bash
# Clone this beauty
git clone https://github.com/marcelo-m7/Scrappers.git
cd Scrappers

# Pick your poison
cd Instaloader  # or cd wordpress

# Install dependencies (check each folder's README)
pip install -r requirements.txt  # or just pip install instaloader for Instagram
```

## 🎯 Use Cases

**For the Instagram Tool:**
- Archiving your own posts before Instagram inevitably changes everything
- Data science projects analyzing visual trends
- Backing up public figure content for research
- Making your designer friend's portfolio accessible offline

**For the WordPress Scraper:**
- Building training datasets for AI models
- Creating offline documentation archives
- Content migration projects
- SEO analysis without clicking through 500 pages

## ⚠️ Legal Disclaimer (The Boring But Important Part)

Look, with great scraping power comes great responsibility:

- **Respect robots.txt** - If a site doesn't want to be scraped, don't scrape it
- **Follow Terms of Service** - Yes, those things you never read
- **Rate limiting is your friend** - Don't DDoS websites accidentally (or intentionally)
- **Personal use is fine, commercial use might not be** - Check the rules
- **Copyright exists** - Just because you can download it doesn't mean you own it

I'm not your lawyer, and this isn't legal advice. Use your brain and don't be evil.

## 🛡️ Features That Make Life Easier

- **Robust Error Handling**: These tools won't crash at the first sign of trouble
- **Progress Tracking**: See what's happening in real-time
- **Resume Capability**: Start where you left off (looking at you, Instaloader)
- **UTF-8 Support**: Because the world speaks more than ASCII
- **Automatic Retries**: Network hiccup? No problem.
- **Clean Output**: Organized files with sensible naming conventions

## 🤝 Contributing

Found a bug? Have an idea for a new scraper? Want to make the code less terrible? PRs are welcome!

Just follow these simple guidelines:
1. Don't break existing functionality (write tests if you're fancy)
2. Keep the code readable (future you will thank present you)
3. Update the documentation (yes, it matters)
4. Match the existing style (consistency is beautiful)

## 📚 Project Structure

```
Scrappers/
├── README.md                  # You are here!
├── Instaloader/              # Instagram image downloader
│   ├── main.py              # The magic happens here
│   ├── README.md            # Detailed Instagram scraper docs
│   └── LICENSE              # Legal stuff
└── wordpress/               # WordPress sitemap scraper
    ├── main.py              # Sitemap parsing wizardry
    ├── README.md            # Detailed WordPress scraper docs
    └── requirements.txt     # Dependencies (requests, beautifulsoup4, lxml)
```

## 🐛 Troubleshooting

**"It's not working!"**
- Did you install the dependencies?
- Is your internet working?
- Did you spell the username correctly?
- Check the error message (I know, revolutionary concept)

**"It's too slow!"**
- Welcome to rate limiting! The tools respect server limits
- Use `--fast-update` for Instagram to skip already-downloaded content
- Patience is a virtue (or grab a coffee ☕)

**"Instagram keeps blocking me!"**
- Use authentication (`--login` or `--sessionid`)
- Don't run it 47 times in a row
- Instagram's anti-bot measures are... enthusiastic

## 🔮 Future Plans (Maybe)

- [ ] Twitter/X scraper (if the API doesn't cost a kidney)
- [ ] Reddit archiver (because some subreddits are gold mines)
- [ ] YouTube metadata extractor (without violating all the rules)
- [ ] LinkedIn scraper (just kidding, that's impossible)
- [ ] Generic scraper framework (for when you want to scrape EVERYTHING)

## 📝 Changelog

### v2.0 - The "Actually Works Now" Release
- WordPress scraper now handles nested sitemap indexes properly
- Added progress tracking with actual numbers
- Fixed directory creation (no more "FileNotFoundError" surprises)
- Removed duplicate code (because DRY isn't just a weather condition)
- Better error handling everywhere
- Added proper type hints (Python 3.6+ appreciation)

### v1.0 - The Beginning
- Initial release with Instagram and WordPress scrapers
- Basic functionality that mostly worked

## 💡 Pro Tips

1. **Start small**: Test with a small profile/site first
2. **Use authentication**: Reduces rate limiting headaches
3. **Check the docs**: Each scraper has detailed instructions in its folder
4. **Be patient**: Good things come to those who wait (and don't hammer APIs)
5. **Back up your data**: Hard drives fail, clouds disappear, entropy is real

## 🙏 Acknowledgments

- Built with [requests](https://requests.readthedocs.io/), [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/), and [instaloader](https://instaloader.github.io/)
- Inspired by procrastination and the desire to automate everything
- Powered by coffee and the occasional existential crisis
- Special thanks to Stack Overflow for raising all of us

## 📬 Contact

Got questions? Found a bug? Want to tell me my code is terrible?

**Marcelo Santos**  
GitHub: [@marcelo-m7](https://github.com/marcelo-m7)

---

<div align="center">

**⭐ If this saved you time, consider starring the repo!**

*Made with ☕ and questionable life choices by Marcelo Santos*

</div>

---

## 📄 License

Check individual tool folders for license information. Generally speaking, use responsibly and don't sue me if your scraping adventures go sideways.

Remember: **With great data comes great responsibility.** 🕷️

---

*P.S. - If you're reading this far, you're either really thorough or really bored. Either way, thanks for stopping by!*
