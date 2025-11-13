# Photos App Integration Guide

**Important:** Photos app doesn't support CSV import. Here are the ACTUAL ways to add keywords to your medical images in Photos app.

## 🎯 Three Ways to Add Keywords

### Method 1: Embed EXIF Metadata (Recommended)

**Best for:** New imports, preserves metadata permanently

Embed keywords directly into image files before importing to Photos:

```bash
# Install exiftool (one-time)
brew install exiftool

# Embed keywords into images
python embed_photos_keywords.py -i /Users/admin/Desktop/MedGraphics -o photos_import

# Import to Photos
# Drag photos_import folder into Photos app
# Keywords are automatically imported!
```

**Advantages:**
- ✅ Keywords permanently embedded in files
- ✅ Survives export/re-import
- ✅ Works with any app that reads EXIF
- ✅ One-time process

**How it works:**
1. Creates copies of your images with embedded EXIF keywords
2. Keywords include: specialty, urgency, topic, key concepts
3. Photos app automatically reads EXIF keywords on import
4. You can search by keyword in Photos

---

### Method 2: AppleScript (For existing Photos)

**Best for:** Images already in Photos app

Add keywords to photos already imported into Photos:

```bash
# Generate and save AppleScript
python add_keywords_to_photos.py -s add_keywords.scpt

# Run the script
osascript add_keywords.scpt
```

**Or run directly:**
```bash
python add_keywords_to_photos.py
```

**Advantages:**
- ✅ Works with existing Photos library
- ✅ No need to re-import
- ✅ Automated batch processing

**How it works:**
1. Searches Photos library for each filename
2. Adds keywords via AppleScript
3. Photos app updates keyword index
4. Search works immediately

---

### Method 3: Manual (Small Collections)

**Best for:** < 20 images, want full control

Manually add keywords in Photos app:

1. **Import images** to Photos app
2. **Select image**
3. **Press Cmd+I** for info panel
4. **Add keywords** in keyword field
5. **Repeat** for each image

Use the reference CSV to know which keywords to add:
```bash
# Generate reference guide
cat output/quick_reference.md
```

---

## 🚀 Quick Start (Recommended Path)

### For New Imports:

```bash
# 1. Install exiftool (if not installed)
brew install exiftool

# 2. Embed keywords
python embed_photos_keywords.py \
  -i /Users/admin/Desktop/MedGraphics \
  -o ~/Desktop/MedicalImages_Tagged

# 3. Import to Photos
# Open Photos app
# Drag ~/Desktop/MedicalImages_Tagged folder into Photos
# Done! Keywords automatically imported

# 4. Test search
# In Photos app, search for "Critical" or "Cardiology"
# Your images appear!
```

### For Existing Photos:

```bash
# 1. Generate AppleScript
python add_keywords_to_photos.py -s add_keywords.scpt

# 2. Review the script (optional)
open -a "Script Editor" add_keywords.scpt

# 3. Run it
osascript add_keywords.scpt

# 4. Test in Photos
# Search for keywords like "Emergency", "Cardiology", etc.
```

---

## 📸 Using Keywords in Photos App

Once keywords are added, you can:

### Search by Keyword:
1. Open Photos app
2. Click search bar (Cmd+F)
3. Type keyword: "Critical", "Cardiology", "STEMI"
4. Relevant images appear instantly

### Create Smart Albums:
1. File → New Smart Album
2. Add rule: "Keyword contains Critical"
3. Auto-updates as you add more images

### Filter by Multiple Keywords:
- Search: "Critical Cardiology" (shows images with both)
- Smart album with multiple rules

### Browse by Keyword:
1. View → Show Sidebar
2. Select "Keywords" in sidebar
3. Browse all your keywords
4. Click any keyword to see those images

---

## 🔍 What Keywords Are Added?

For each image, these keywords are added:

1. **Specialty** - e.g., "Cardiology", "Neurology"
2. **Urgency** - e.g., "Critical", "High", "Medium", "Low"
3. **Topic** - e.g., "STEMI Management", "Stroke Protocol"
4. **Use Case** - e.g., "Emergency", "Routine Care"
5. **Target Audience** - e.g., "ED Physician", "ICU Nurse"
6. **Key Concepts** (up to 10) - e.g., "ECG Interpretation", "Time-sensitive"

**Example:**
For a cardiac emergency image, keywords might be:
- Cardiology
- Critical
- STEMI Management
- Emergency
- ED Physician
- ECG Interpretation
- Time to Intervention
- Door to Balloon Time

---

## 💡 Pro Tips

### Organize with Albums

Create albums for quick access:

```
Medical Images/
├── Critical Protocols/
├── Cardiology/
├── Neurology/
├── Emergency Medicine/
└── ICU Protocols/
```

### Use Smart Albums

**Critical Cases:**
- Keyword contains "Critical"

**By Specialty:**
- Keyword contains "Cardiology"

**ED Quick Reference:**
- Keyword contains "Emergency" AND "Critical"

### Combine with Other Metadata

Photos app also imports:
- **Title** - Set to the topic (e.g., "STEMI Management")
- **Description** - Content summary
- **Subject** - Specialty

You can search across all fields!

---

## 🛠️ Troubleshooting

### exiftool not found

```bash
# Install via Homebrew
brew install exiftool

# Or download from https://exiftool.org/
```

### Keywords not showing in Photos

After running the script:
1. Quit Photos app completely
2. Reopen Photos
3. Select an image
4. Press Cmd+I
5. Keywords should appear

### AppleScript permission denied

1. System Preferences → Security & Privacy → Privacy
2. Select "Automation"
3. Enable Terminal/Python for Photos app
4. Run script again

### Can't find images in AppleScript

Make sure filenames match exactly:
- AppleScript searches by filename
- Case-sensitive
- Include extension in taxonomy if needed

### Too slow for many images

For 100+ images:
1. Save AppleScript to file: `-s script.scpt`
2. Run overnight
3. Or use EXIF method (faster)

---

## 📊 Comparison

| Method | Speed | Best For | Permanent? |
|--------|-------|----------|------------|
| **EXIF Embed** | Fast | New imports | ✅ Yes |
| **AppleScript** | Slow | Existing photos | Tied to library |
| **Manual** | Very Slow | Small collections | Tied to library |

**Recommendation:**
- **New workflow:** Use EXIF embed
- **Existing photos:** Use AppleScript
- **< 10 images:** Manual is fine

---

## 🎯 Complete Workflow

**Step 1: Organize images**
```bash
python medical_image_organizer.py /Users/admin/Desktop/MedGraphics
```

**Step 2: Embed keywords**
```bash
python embed_photos_keywords.py \
  -i /Users/admin/Desktop/MedGraphics \
  -o ~/Desktop/Tagged_Medical_Images
```

**Step 3: Import to Photos**
- Drag `~/Desktop/Tagged_Medical_Images` into Photos app

**Step 4: Create smart albums** (optional)
- Critical Protocols
- By Specialty
- Emergency Reference

**Step 5: Search and use!**
- Search by keyword
- Quick bedside reference
- Always with you on iPhone (if iCloud Photos enabled)

---

## 📱 Bonus: iPhone Access

If you use iCloud Photos:

1. ✅ Keywords sync to iPhone automatically
2. ✅ Search works on iPhone Photos app
3. ✅ No extra setup needed
4. ✅ Offline after initial sync

**On iPhone:**
1. Open Photos app
2. Tap Search
3. Type "Critical" or "Cardiology"
4. Your medical images appear!

Combined with the native iOS app, you have:
- **Photos app** - For browsing by keyword
- **MedAssist app** - For advanced search and clinical queries

---

## ❓ FAQ

**Q: Will keywords be lost if I export images?**
A: EXIF-embedded keywords stay with the file. Library keywords don't.

**Q: Can I edit keywords later?**
A: Yes, in Photos app info panel (Cmd+I)

**Q: Do keywords take up extra space?**
A: Negligible (few KB per image)

**Q: Can I remove keywords?**
A: Yes, select image → Info → Delete keywords

**Q: Will this work with Lightroom?**
A: EXIF keywords yes, AppleScript no (Photos-specific)

---

## 🎉 Summary

**For most users:**
```bash
brew install exiftool
python embed_photos_keywords.py -i /path/to/images -o tagged_images
# Drag tagged_images into Photos app
# Search by keyword!
```

**Quick reference while working:**
- Search "Critical" for urgent protocols
- Search "Cardiology" for heart-related
- Search "Emergency" for ED protocols

**Your medical images are now searchable and organized in Photos app!** 🏥📸
