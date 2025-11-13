# MedAssist - Native iOS App

Native iOS medical image search app with offline support and optional AI-powered queries.

## Features

- ✅ **100% Native iOS** - Built with SwiftUI
- ✅ **Offline-First** - Works without internet
- ✅ **Fast Search** - Instant local keyword matching
- ✅ **AI Mode** - Optional Claude API integration for smart queries
- ✅ **Image Viewing** - Full-screen viewing with zoom
- ✅ **Dark Mode** - Automatic dark/light mode support
- ✅ **iOS Design** - Native iOS UI/UX

## Requirements

- **Xcode 15.0+**
- **iOS 17.0+** (or 16.0+ with minor modifications)
- **Swift 5.9+**

## Setup Instructions

### 1. Prepare Your Data

First, organize your medical images using the Python tool:

```bash
# From the main MedAssist directory
python medical_image_organizer.py /Users/admin/Desktop/MedGraphics
```

This creates `output/taxonomy_discovery.json` with all image metadata.

### 2. Copy Files to iOS Project

```bash
# Copy taxonomy JSON
cp output/taxonomy_discovery.json ios-app/MedAssist/MedAssist/taxonomy.json

# Copy images to iOS project
cp /Users/admin/Desktop/MedGraphics/* ios-app/MedAssist/MedAssist/Images/
```

### 3. Open in Xcode

```bash
cd ios-app/MedAssist
open MedAssist.xcodeproj
```

Or double-click `MedAssist.xcodeproj` in Finder.

### 4. Add Files to Xcode

1. In Xcode, right-click on "MedAssist" folder
2. Select "Add Files to MedAssist..."
3. Add `taxonomy.json`
4. Add all images from `Images/` folder
5. Make sure "Copy items if needed" is checked
6. Select "MedAssist" target

### 5. Configure API Key (Optional - for AI mode)

Edit `Services/ClaudeService.swift`:

```swift
private let apiKey = "your-api-key-here"
```

Or add to your Xcode scheme as an environment variable.

### 6. Build and Run

1. Select your device or simulator
2. Press Cmd+R or click Play button
3. App installs and launches!

## App Structure

```
MedAssist/
├── MedAssistApp.swift          # App entry point
├── Models/
│   ├── MedicalImage.swift      # Image data model
│   └── Taxonomy.swift          # Taxonomy data model
├── Views/
│   ├── ContentView.swift       # Main search view
│   ├── SearchBar.swift         # Search input
│   ├── ImageCard.swift         # Image result card
│   ├── ImageDetailView.swift  # Full-screen image view
│   └── FiltersView.swift       # Quick filters
├── Services/
│   ├── SearchService.swift     # Offline search logic
│   ├── ClaudeService.swift     # AI query service (optional)
│   └── DataLoader.swift        # Load JSON data
└── Resources/
    ├── taxonomy.json           # Your image metadata
    └── Images/                 # Your medical images
```

## How to Use

### Basic Search

1. **Open app** - Shows all images
2. **Type keywords** - Instant filtering
3. **Tap image** - Full-screen view with pinch-to-zoom
4. **Tap filters** - Quick specialty/urgency filters

### AI Query Mode (Optional)

1. **Tap AI button** - Switch to AI mode
2. **Type clinical scenario**:
   ```
   Patient 3 days post bowel surgery with fever
   and elevated WBC. What should I review?
   ```
3. **Get smart results** - AI understands context
4. **View explanations** - See why each image is relevant

## Customization

### Change Colors

Edit `Views/ContentView.swift`:

```swift
Color.purple  // Change app theme color
```

### Modify Search Logic

Edit `Services/SearchService.swift`:

```swift
func search(_ query: String) -> [MedicalImage] {
    // Customize search algorithm
}
```

### Add Features

- **Favorites**: Add CoreData to save favorites
- **Notes**: Let users add notes to images
- **Export**: Share images via iOS share sheet
- **Sync**: Add iCloud sync

## Offline vs Online Modes

### Offline Mode (Default)
- ✅ No internet required
- ✅ Instant search
- ✅ Private - data stays on device
- ❌ Simple keyword matching only

### Online AI Mode (Optional)
- ❌ Requires internet
- ✅ Smart query understanding
- ✅ Clinical reasoning
- ✅ Relevance scoring
- 💰 Costs ~$0.01-0.03 per query

## Performance Tips

### Image Optimization

Before adding to Xcode, optimize images:

```bash
# Reduce image size (optional)
for img in Images/*.{jpg,png}; do
    sips -Z 1200 "$img"  # Max dimension 1200px
done
```

### Asset Catalog

For better performance:
1. Create Asset Catalog in Xcode
2. Add images to catalog
3. Xcode automatically optimizes for iOS

## Distribution

### TestFlight (Beta Testing)

1. Archive app: Product → Archive
2. Upload to App Store Connect
3. Add testers in TestFlight
4. Share app with colleagues!

### Personal Use

1. Connect iPhone to Mac
2. Select your device in Xcode
3. Build and run
4. App installs on your phone
5. Trust developer certificate in Settings

### App Store (Full Release)

1. Join Apple Developer Program ($99/year)
2. Complete app metadata
3. Submit for review
4. Publish to App Store!

## Troubleshooting

### "taxonomy.json not found"

Make sure file is added to Xcode project:
- Right-click project
- Add Files
- Select taxonomy.json
- Check "Copy items if needed"
- Select target

### Images not showing

1. Check images are in project
2. Verify filenames match taxonomy.json
3. Check images are added to target

### Build errors

1. Check Xcode version (15.0+)
2. Check deployment target (iOS 17.0+)
3. Clean build folder: Shift+Cmd+K
4. Restart Xcode

### API key not working

1. Check key in ClaudeService.swift
2. Verify key starts with "sk-ant-"
3. Check internet connection
4. Test with simple query first

## Advanced Features

### Push Notifications

Add reminders for protocol reviews:

```swift
import UserNotifications

// Request permission and schedule
```

### Widget Support

Add home screen widget showing critical protocols:

```swift
import WidgetKit

// Create widget extension
```

### Siri Integration

Enable voice search:

```swift
import Intents

// Add Siri shortcuts
```

### Apple Watch App

Quick reference on your wrist:

```swift
// Create watchOS target
```

## FAQ

**Q: Can I use this without a Mac?**
A: No, you need Xcode which only runs on Mac.

**Q: Can I build this with React Native or Flutter?**
A: Yes! The concepts translate. The Python backend generates JSON that any mobile framework can use.

**Q: How much space does it take?**
A: Base app: ~10MB. Plus your images (typically 1-5MB each).

**Q: Can I share with colleagues?**
A: Yes! Use TestFlight for easy distribution.

**Q: Does it work on iPad?**
A: Yes! The SwiftUI code is universal.

**Q: Offline AI possible?**
A: Yes, but requires CoreML model. Complex to setup.

## Next Steps

1. **Build the app** - Follow setup instructions above
2. **Test it** - Try on your iPhone
3. **Customize** - Add your own features
4. **Share it** - TestFlight to colleagues
5. **Enhance it** - Add widgets, Siri, etc.

## Support

- Check `Models/` for data structures
- Check `Views/` for UI components
- Check `Services/` for business logic
- See main README.md for Python tools

## License

Same as main MedAssist project - use freely!

---

**Ready to build your native iOS medical reference app!** 📱🏥
