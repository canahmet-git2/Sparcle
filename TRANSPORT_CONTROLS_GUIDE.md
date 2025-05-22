# Transport Controls and Spine-Style UI Guide

## What Are Transport Controls?

The transport controls are the playback navigation buttons you see in professional animation software like Spine, After Effects, and Blender. They allow you to navigate through your animation timeline quickly and efficiently.

### Transport Button Functions:

1. **|<<** - **Previous Key**: Jump to the previous keyframe
2. **<** - **Previous Frame**: Go back one frame  
3. **Play** - **Play/Pause**: Start or stop animation playback
4. **>** - **Next Frame**: Go forward one frame
5. **>>|** - **Next Key**: Jump to the next keyframe

These replace the old unicode symbols (◀◀ ◀ ▶ ▶ ▶▶) that weren't displaying correctly.

## New Spine-Style Separated UI

### Timeline Section (Top Panel)
- **Background**: Dark gray (#3A3A3A) with borders
- **Contains**: Transport controls, time display, timeline slider, keyframe buttons
- **Purpose**: Animation playback and navigation controls
- **Height**: 60dp for comfortable button access

### Dopesheet Section (Bottom Panel)  
- **Background**: Darker gray (#2A2A2A) with borders
- **Contains**: Keyframe tracks, parameter visualization, scrollable timeline
- **Purpose**: Keyframe editing and parameter animation display
- **Height**: 100dp for multiple parameter tracks

### Visual Separation
- **Distinct Backgrounds**: Different shades to clearly separate sections
- **Bordered Panels**: Gray borders (#555555) around each section
- **Header Bars**: Each section has its own labeled header
- **Professional Layout**: Matches Spine's industry-standard interface design

## How to Use the New Interface

### Timeline Section Controls:
1. **Transport Controls**: Use |<< < Play > >>| to navigate through animation
2. **Time Display**: Shows current time in "seconds:frames (Frame#)" format
3. **Timeline Slider**: Scrub through animation by dragging
4. **Auto Key**: Toggle automatic keyframe creation (red when active)
5. **Key Button**: Manually create keyframes for all parameters
6. **Del Button**: Delete keyframes (future functionality)

### Dopesheet Section:
1. **Parameter Tracks**: Each parameter gets its own horizontal track
2. **Color-Coded Keyframes**: Different colors for different parameters:
   - 🟢 **Emission Rate**: Bright Green
   - 🔵 **Lifespan**: Bright Blue  
   - 🟠 **Particle Color**: Bright Orange
   - 🟣 **Initial Velocity**: Magenta
   - 🔴 **Emitter Position**: Bright Red
3. **Horizontal Scrolling**: Navigate through long animations
4. **Frame Ruler**: Shows frame numbers and time marks

## Professional Workflow Benefits

### 1. **Familiar Interface**
- Matches industry-standard tools (Spine, After Effects, Maya)
- Reduced learning curve for professional animators
- Consistent with animation software conventions

### 2. **Clear Visual Hierarchy**
- Separated sections prevent confusion
- Distinct purposes for each panel
- Professional color scheme

### 3. **Efficient Navigation**
- Quick keyframe jumping with transport controls
- Frame-accurate stepping with < > buttons
- Visual feedback for current position

### 4. **Parameter Organization**
- Each parameter type has its own track
- Color coding for instant identification
- No overlapping keyframes

## Comparison to Spine

### Similarities Achieved:
✅ **Separated Timeline/Dopesheet panels**  
✅ **Transport control buttons**  
✅ **Professional time format**  
✅ **Parameter track system**  
✅ **Bordered panel design**  
✅ **Color-coded keyframes**  
✅ **Auto Key functionality**  

### Future Enhancements:
- 🔄 **Keyframe selection and editing**
- 🔄 **Curve editor integration**  
- 🔄 **Onion skinning**
- 🔄 **Timeline zoom controls**
- 🔄 **Parameter grouping**

## Technical Implementation

### Layout Structure:
```
TimelinePanel
├── Timeline Section (60dp)
│   ├── Timeline Header (20dp)
│   └── Timeline Controls (35dp)
│       ├── Transport Controls (25%)
│       ├── Time Display (15%)
│       ├── Timeline Slider (40%)
│       └── Key Controls (20%)
└── Dopesheet Section (100dp)
    ├── Dopesheet Header (20dp)
    └── Scrollable Content (75dp)
        ├── Frame Numbers (25dp)
        └── Keyframe Tracks (50dp)
```

### Color Scheme:
- **Timeline Background**: #3A3A3A (darker)
- **Dopesheet Background**: #2A2A2A (darkest)  
- **Headers**: #2C2C2C / #1C1C1C
- **Borders**: #555555
- **Auto Key Active**: #FF3333 (bright red)
- **Auto Key Inactive**: #808080 (gray)

This professional interface transforms Sparcle into a production-ready animation tool that rivals industry-standard software like Spine Pro. 