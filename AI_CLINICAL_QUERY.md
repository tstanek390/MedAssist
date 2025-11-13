# AI Clinical Query - Intelligent Search Guide

Search your medical images using natural language clinical scenarios. The AI understands complex queries and finds the most relevant images to help you.

## 🤖 What's Different?

**Standard Search** (`web_search.py`):
- Keyword matching (e.g., "cardiology", "critical")
- Fast, simple, no AI processing
- Good for: "I know what I'm looking for"

**AI Clinical Query** (`web_search_ai.py`):
- Natural language understanding
- Analyzes clinical scenarios
- Explains WHY each image is relevant
- Good for: "I have a clinical situation and need guidance"

## 🚀 Quick Start

### Setup (One-time)
```bash
# Install dependencies
pip install flask anthropic

# Set API key
export ANTHROPIC_API_KEY='your-key-here'
```

### Start the AI Search Server
```bash
# Using startup script
./start_ai_search.sh /Users/admin/Desktop/MedGraphics

# Or directly
python web_search_ai.py -i /Users/admin/Desktop/MedGraphics
```

### Access from iPhone
```
Safari → http://YOUR-MAC-IP:5002
```

Note: Uses port 5002 by default (vs 5001 for standard search)

## 💬 How to Query

### Write Natural Language Queries

**Instead of keywords like:**
- "fever postop"
- "chest pain cardiac"

**Write clinical scenarios:**
- "Patient on postoperative day 3 after bowel surgery has fever and abdominal pain. What should I check?"
- "Patient with chest pain and elevated troponin, what protocols should I follow?"
- "Acute onset left-sided weakness, suspected stroke. Need rapid assessment guidelines."

### Example Queries

**Postoperative Complications:**
```
Patient 3 days post laparoscopic bowel resection presenting with
fever (38.5°C), abdominal tenderness, and elevated CRP with
leukocytosis. Concerned about anastomotic leak. What imaging
and protocols should I review?
```

**Cardiac Emergencies:**
```
65yo male with crushing chest pain for 2 hours, diaphoresis,
elevated troponin. Need STEMI protocol and ECG interpretation
guidelines.
```

**Stroke Protocol:**
```
72yo female with sudden onset right-sided weakness and slurred
speech 1 hour ago. Need acute stroke assessment and treatment
protocol.
```

**Sepsis Management:**
```
Patient with suspected sepsis: fever, hypotension, tachycardia,
lactate 4.0. Need sepsis bundle and resuscitation protocols.
```

**ICU Procedures:**
```
Need to perform emergency intubation in ICU for respiratory
failure patient. Looking for RSI protocol and equipment checklist.
```

## 🎯 AI Results Include

For each relevant image, the AI provides:

1. **Relevance Score** (0-100%)
   - How relevant to your scenario
   - Visual bar for quick scanning

2. **Clinical Reasoning**
   - WHY this image helps your case
   - Specific clinical connection explained

3. **Key Sections to Review**
   - What parts of the image to focus on
   - Specific recommendations

4. **Standard Metadata**
   - Specialty, urgency, topic
   - Key concepts covered

## 📱 Mobile Interface Features

**Optimized for Clinical Use:**
- ✓ Large text area for detailed scenarios
- ✓ Clear relevance scoring
- ✓ Tap to view full-screen images
- ✓ Example queries for quick start
- ✓ Cmd/Ctrl+Enter to search quickly

**Visual Indicators:**
- Green relevance bar (width = relevance %)
- Color-coded urgency badges
- Blue reasoning boxes
- Clear section highlights

## 🔬 How It Works

1. **You describe** the clinical scenario
2. **AI analyzes** your query and understands:
   - The medical condition
   - What information you need
   - Clinical urgency/context
3. **AI reviews** all your images and their content
4. **AI matches** relevant images to your scenario
5. **AI explains** why each image is helpful
6. **Results ranked** by relevance

## 💡 Pro Tips

### Write Better Queries

**Be specific:**
- ✓ Include timeline (day 3 postop, 2 hours ago)
- ✓ Include vitals/labs if relevant (fever 38.5, lactate 4.0)
- ✓ Describe what you need (protocol, guidelines, assessment)

**Include context:**
- ✓ Patient type (elderly, postop, trauma)
- ✓ Clinical setting (ED, ICU, ward)
- ✓ Your concern or question

**Examples of good queries:**
```
❌ "sepsis"
✓ "Need sepsis protocol for hypotensive patient with elevated lactate"

❌ "heart"
✓ "Chest pain patient with ST elevation on ECG, need STEMI activation protocol"

❌ "stroke"
✓ "Acute stroke presenting within 3 hours, eligible for thrombolysis?"
```

### Use Example Queries

- Tap the example queries to get started
- Modify them for your specific case
- See how the AI responds to learn the style

### Combine with Standard Search

- Use **AI search** when you have a complex scenario
- Use **standard search** when you know exactly what you want
- Both can run simultaneously (different ports)

## ⚙️ Technical Details

### Requirements
- Anthropic API key
- Internet connection (for AI processing)
- Flask installed
- Taxonomy file from initial image analysis

### Cost
- ~$0.01-0.03 per query (depending on complexity)
- Much cheaper than re-analyzing images
- Real-time clinical decision support value

### Performance
- Query processing: 2-10 seconds (AI thinking time)
- More complex queries take slightly longer
- Locally cached images load instantly

### Privacy
- Queries go to Anthropic's Claude API
- Images stay on your local network
- No PHI should be in queries (use generic descriptions)

## 🔐 PHI Considerations

**Important**: Don't include patient identifiers in queries!

**Bad:**
```
❌ "John Smith age 45 with chest pain"
```

**Good:**
```
✓ "45yo male with chest pain and elevated troponin"
```

The AI doesn't need and shouldn't receive:
- Patient names
- MRN/account numbers
- Specific dates
- Location identifiers

Generic clinical descriptions work perfectly!

## 🛠️ Command Line Options

```bash
python web_search_ai.py \
  -i /path/to/images \           # Required: Image directory
  -t output/taxonomy.json \      # Taxonomy file
  -k YOUR_API_KEY \              # API key (or use env var)
  -p 5002 \                      # Port number
  --host 0.0.0.0                 # Network binding
```

## 🔄 Running Both Search Interfaces

You can run both simultaneously:

```bash
# Terminal 1: Standard keyword search
./start_web_search.sh /path/to/images
# Access at: http://YOUR-IP:5001

# Terminal 2: AI clinical query
./start_ai_search.sh /path/to/images
# Access at: http://YOUR-IP:5002
```

Use whichever fits your need at the moment!

## 🆘 Troubleshooting

### AI Search Not Working

**API Key Error:**
```bash
# Make sure key is set
echo $ANTHROPIC_API_KEY

# Or pass directly
python web_search_ai.py -i /path/to/images -k 'your-key'
```

**Taking Too Long:**
- Complex queries may take 5-10 seconds
- This is normal for AI processing
- Be patient!

**No Results:**
- Try simpler, more general query
- Check that your images cover that topic
- Review taxonomy_summary.txt to see what's available

**Connection Failed:**
- Check internet connection (needed for AI)
- Verify API key has credits
- Try standard search as fallback

### Relevance Scores Low

If all results show low relevance (< 50%):
- Your images may not cover this topic well
- Try broader medical specialty terms
- Check what images you actually have

### AI Gives Wrong Reasoning

The AI matches based on your taxonomy data:
- If image descriptions are incomplete, matches may be off
- Original image analysis quality matters
- You can re-run the organizer for better taxonomy

## 📊 Comparison Table

| Feature | Standard Search | AI Clinical Query |
|---------|----------------|-------------------|
| **Speed** | Instant | 2-10 seconds |
| **Cost** | Free | ~$0.01-0.03/query |
| **Understanding** | Keywords only | Clinical scenarios |
| **Reasoning** | Shows matches | Explains relevance |
| **Best For** | Quick lookup | Complex cases |
| **Internet** | Not needed | Required |
| **Query Style** | "cardiology STEMI" | "chest pain protocol" |

## ✨ Advanced Usage

### Background Running
```bash
# Run AI search in background
nohup python web_search_ai.py -i /path/to/images > ai_search.log 2>&1 &
```

### Custom Port
```bash
# Avoid conflicts
python web_search_ai.py -i /path/to/images -p 8080
```

### Multiple Collections
```bash
# ED protocols on 5002
python web_search_ai.py -i ~/ED_Images -p 5002

# ICU protocols on 5003
python web_search_ai.py -i ~/ICU_Images -p 5003
```

## 🎓 Learning the System

**Week 1: Start Simple**
- Use example queries
- See what results you get
- Learn the query style

**Week 2: Real Scenarios**
- Use during actual clinical work
- Refine your query writing
- Note what works best

**Week 3: Optimize**
- Know when to use AI vs keyword search
- Develop quick query templates
- Add to home screen for instant access

## 📈 Query Success Tips

**Successful queries usually include:**
1. Clinical context (postop, trauma, acute)
2. Time frame (day 3, within 2 hours)
3. Key findings (fever, elevated labs, pain)
4. What you need (protocol, guidelines, assessment)

**Pattern:**
"[Patient context] with [key findings] [timeframe]. Need [what you're looking for]."

---

## Summary

**Start the server:**
```bash
export ANTHROPIC_API_KEY='your-key'
./start_ai_search.sh /Users/admin/Desktop/MedGraphics
```

**Access from iPhone:**
```
http://YOUR-MAC-IP:5002
```

**Example query:**
```
Patient 3 days post bowel surgery with fever, abdominal pain,
and elevated WBC. Concerned about anastomotic leak. What
imaging and management protocols should I review?
```

**Get intelligent, context-aware results!** 🎯

---

**Questions?** Check:
- MOBILE_SEARCH.md - For standard keyword search
- STANDALONE_USAGE.md - For initial image organization
- README.md - For complete documentation
