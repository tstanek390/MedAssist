# Mobile Search - iPhone Access Guide

Quick search your medical images from your iPhone with a simple web interface.

## 🚀 Quick Start

### 1. Install Flask (One-time)
```bash
pip install flask
```

### 2. Start the Server on Your Mac
```bash
# Using the startup script
./start_web_search.sh /Users/admin/Desktop/MedGraphics

# Or directly with Python
python web_search.py -i /Users/admin/Desktop/MedGraphics
```

### 3. Access from Your iPhone

The server will display the URL to access from your iPhone. Example:
```
📱 Access from your iPhone:
   http://192.168.1.100:5001
```

Open Safari on your iPhone and go to that URL.

## 📱 Using the Interface

### Search Options

**Type in the search box:**
- Medical specialty: "cardiology", "neurology"
- Urgency level: "critical", "high"
- Condition/topic: "STEMI", "stroke", "sepsis"
- Procedures: "ECG", "intubation"
- Any keyword from your images

**Quick filter buttons:**
- Tap pre-defined filters for instant search
- Filters: Critical, Emergency, Cardiology, Neurology, Protocol, Diagnosis

### Viewing Images

- **Tap any image** to view full screen
- **Pinch to zoom** on full screen image
- **Tap X or outside** to close

### Results Show

Each result displays:
- ✓ Image preview
- ✓ Topic/title
- ✓ Urgency badge (color-coded)
- ✓ Specialty badge
- ✓ Brief summary
- ✓ Why it matched your search

## 🔧 Setup Details

### Full Command Options

```bash
python web_search.py \
  -i /path/to/images \           # Required: Your image directory
  -t output/taxonomy.json \      # Optional: Taxonomy file
  -p 5001 \                      # Optional: Port (default: 5001)
  --host 0.0.0.0                 # Optional: Allow network access
```

### Network Requirements

**Both devices must be on the same WiFi network:**
- ✓ Mac running the server
- ✓ iPhone accessing the interface

**Find your Mac's IP address:**
```bash
# macOS
ipconfig getifaddr en0

# Or the script shows it automatically when starting
```

### Firewall Settings

If you can't connect from iPhone, allow the port through firewall:

**macOS:**
1. System Preferences → Security & Privacy → Firewall
2. Firewall Options
3. Add Python or allow incoming connections

## 💡 Usage Examples

### Example 1: Emergency Shift
```
Start server before your shift:
  ./start_web_search.sh /Users/admin/Desktop/MedGraphics

On iPhone during shift:
  1. Open Safari → http://192.168.1.100:5001
  2. Search "critical"
  3. Quick access to all critical protocols
```

### Example 2: Quick Reference
```
Need cardiology info:
  1. Type "cardiology" or "STEMI"
  2. View matching images instantly
  3. Tap for full screen detail
```

### Example 3: Specific Condition
```
Looking for stroke protocol:
  1. Type "stroke"
  2. See all stroke-related images
  3. Filter by urgency if needed
```

## 📲 Add to iPhone Home Screen

Make it even quicker to access:

1. Open the search page in Safari
2. Tap the Share button
3. Select "Add to Home Screen"
4. Name it "Med Search" or similar
5. Now you have a one-tap icon!

## 🎨 Features

**Mobile-Optimized:**
- ✓ Responsive design for iPhone
- ✓ Touch-friendly interface
- ✓ Fast image loading
- ✓ Swipeable quick filters
- ✓ Full-screen image viewing

**Smart Search:**
- ✓ Searches across all fields
- ✓ Relevance scoring
- ✓ Shows why each image matched
- ✓ Instant results

**User-Friendly:**
- ✓ Color-coded urgency badges
- ✓ Clear result organization
- ✓ No login required
- ✓ Works offline (local network)

## 🔒 Security Notes

- Server runs on local network only (not internet-accessible)
- No data leaves your network
- Firewall-friendly (single port)
- No authentication needed (private network)

## 🛠️ Troubleshooting

### Can't Connect from iPhone

**Check WiFi:**
```bash
# Make sure iPhone is on same network as Mac
# Check Mac's IP: ipconfig getifaddr en0
```

**Try Different Port:**
```bash
# If 5001 is blocked, try another port
python web_search.py -i /path/to/images -p 8080
```

**Check Firewall:**
- Temporarily disable Mac firewall to test
- If it works, add exception for Python/port

### Server Won't Start

**Port Already in Use:**
```bash
# Kill existing process
lsof -ti:5001 | xargs kill -9

# Or use different port
python web_search.py -i /path/to/images -p 5002
```

**Missing Taxonomy:**
```bash
# Run organizer first
python medical_image_organizer.py /path/to/images
```

### Images Not Loading

**Wrong Image Directory:**
```bash
# Make sure path matches where you ran the organizer
python web_search.py -i /Users/admin/Desktop/MedGraphics
```

**File Permissions:**
```bash
# Ensure Python can read images
chmod -R +r /Users/admin/Desktop/MedGraphics
```

### Search Returns No Results

**Case Sensitivity:**
- Search is case-insensitive, so "STEMI" = "stemi"

**Try Broader Terms:**
- Instead of "myocardial infarction" try "cardiac"
- Use specialty names: "cardiology", "neurology"

**Check Taxonomy:**
```bash
# See what was discovered
cat output/taxonomy_summary.txt
```

## 🔄 Keeping It Running

### Background Process (Advanced)

**Run in background:**
```bash
nohup python web_search.py -i /Users/admin/Desktop/MedGraphics > search.log 2>&1 &
```

**Stop background process:**
```bash
# Find process ID
ps aux | grep web_search.py

# Kill it
kill <PID>
```

### Auto-start on Login (Advanced)

Create a LaunchAgent to start automatically:
```bash
# Create plist file at ~/Library/LaunchAgents/com.medassist.search.plist
# (Advanced users only - ask if needed)
```

## 📊 Performance

- **Startup time**: ~1 second
- **Search speed**: Instant (< 100ms)
- **Image loading**: Fast (local files)
- **Concurrent users**: Supports multiple devices

## 🆘 Need Help?

**Quick diagnostics:**
```bash
# Test locally first
open http://localhost:5001

# Check if server is running
lsof -i :5001

# View server logs
# (Logs show in terminal where you started it)
```

**Common issues solved:**
1. Wrong IP? Check: `ipconfig getifaddr en0`
2. Can't connect? Check: Same WiFi network
3. No images? Check: Image directory path
4. No results? Check: Search terms match taxonomy

## 💪 Advanced Usage

### Custom Port
```bash
python web_search.py -i /path/to/images -p 8080
```

### Multiple Collections
```bash
# ED protocols
python web_search.py -i ~/ED_Images -p 5001

# ICU protocols
python web_search.py -i ~/ICU_Images -p 5002
```

### Remote Access (Use with Caution)
```bash
# Expose to internet (requires port forwarding)
# NOT RECOMMENDED - no authentication
python web_search.py -i /path/to/images --host 0.0.0.0
```

## ✨ Pro Tips

1. **Bookmark it**: Add to iPhone favorites for quick access
2. **Home screen icon**: Feels like a native app
3. **Search shortcuts**: Use quick filters for common searches
4. **Full screen**: Tap images for detailed view
5. **Keep server running**: Leave Mac on during work hours

---

## Summary

**Setup once:**
```bash
pip install flask
```

**Start server:**
```bash
./start_web_search.sh /Users/admin/Desktop/MedGraphics
```

**Access from iPhone:**
```
Safari → http://YOUR-MAC-IP:5001
```

**Search and view!** 🎉

---

**Questions?** Check the main README.md or STANDALONE_USAGE.md for more details.
