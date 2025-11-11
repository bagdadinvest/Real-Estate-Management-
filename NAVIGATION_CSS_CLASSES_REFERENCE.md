# Navigation CSS Classes Reference

## Header Area Structure

```
.header-area (container)
├── .header-sticky (when scrolled)
├── .background-header (with background)
└── .container (Bootstrap)
    └── .row
        └── .col-12
            └── .main-nav (Flexbox container)
                ├── .logo
                │   └── h1 (VL)
                ├── ul.nav (Flex items)
                │   ├── li
                │   │   └── a (nav link)
                │   ├── li
                │   │   └── a
                │   ├── li
                │   │   └── a
                │   ├── li
                │   │   └── a
                │   └── li (last-child - Special button)
                │       └── a
                │           └── i (icon)
                ├── .language-switcher
                │   └── .lang-switcher
                │       ├── .lang-current (button)
                │       │   ├── img.flag
                │       │   ├── span.code
                │       │   └── span.chev
                │       └── .lang-menu (dropdown)
                │           └── .lang-item (form)
                │               └── button
                │                   ├── img.flag
                │                   └── span.label
                └── .menu-trigger (hamburger menu)
```

## CSS Properties Applied at Each Level

### `.header-area`
```css
padding: 0px 15px;        /* Mobile override: was 0 initially */
height: 100px;            /* Desktop height */
box-shadow: 0 0 15px ...  /* Background header state */
text-align: center;       /* Mobile override */

/* Responsive overrides:
   1200px: height: 100px
   992px:  height: auto, padding: 10px 0
   768px:  height: auto, padding: 10px 0
   767px:  height: 80px (legacy)
*/
```

### `.main-nav` (Flexbox Parent)
```css
background: transparent;
display: flex;
align-items: center;       /* Vertically center all items */
flex-direction: row;       /* Desktop: horizontal */
flex-wrap: nowrap;         /* Desktop: no wrapping */

/* Responsive overrides:
   992px:  flex-wrap: wrap, padding: 15px 0
   768px:  flex-direction: column, align-items: stretch
*/
```

### `.logo`
```css
display: inline-block;
flex-shrink: 0;            /* Never shrink */
transition: all 0.3s ease;

h1 {
  line-height: 100px;      /* Desktop */
  font-size: 28px;         /* Desktop */
  text-transform: uppercase;
  color: #1e1e1e;
  font-weight: 700;
  letter-spacing: 2px;
  
  /* Responsive sizes:
     1400px: line-height: 100px, font-size: 28px
     1200px: line-height: 80px, font-size: 24px
     992px:  line-height: 60px, font-size: 22px
     768px:  line-height: 50px, font-size: 20px
  */
}
```

### `ul.nav` (Nav Items Container)
```css
flex-basis: auto;          /* Don't take full width */
margin-top: 30px;          /* Desktop vertical offset */
margin-right: auto;        /* Push language switcher right */
margin-left: 0;            /* Reset */
margin-bottom: 0;          /* Reset */
padding-left: 0;           /* Reset */
justify-content: flex-start; /* Left-aligned */
gap: 0;                    /* No extra spacing */
list-style: none;          /* Remove bullets */
display: flex;
align-items: center;
z-index: 999;

/* Responsive overrides:
   1400px: margin-top: 20px
   1200px: margin-top: 15px (via .nav li)
   992px:  flex-basis: 100%, margin-top: 15px, justify-content: center
   768px:  flex-basis: 100%, margin-top: 0, justify-content: center
*/
```

### `li` (Nav Items)
```css
padding-left: 10px;        /* Desktop horizontal padding */
padding-right: 10px;       /* Desktop horizontal padding */
height: 100px;             /* Desktop height for centered link */
line-height: 100px;        /* Desktop centering */

a {
  display: block;
  padding-left: 20px;      /* Desktop text padding */
  padding-right: 20px;     /* Desktop text padding */
  font-weight: 500;
  font-size: 15px;         /* Desktop font */
  height: 40px;            /* Link actual height */
  line-height: 40px;       /* Link text centering */
  text-transform: capitalize;
  color: #1e1e1e;
  border: transparent;
  letter-spacing: 0.25px;
  transition: all 0.4s ease;
  
  /* Responsive sizes:
     1400px: font-size: 14px, padding: 16px
     1200px: font-size: 13px, padding: 12px, height: 35px
     992px:  font-size: 12px, padding: 10px, height: 32px
     768px:  font-size: 11px, padding: 8px, height: 30px
  */
  
  &:hover {
    color: #f35525;        /* Orange hover */
  }
  
  &.active {
    color: #f35525;        /* Orange active state */
  }
}

li:last-child a {          /* Special button style */
  background-color: #1e1e1e; /* Black background */
  color: #fff;
  font-size: 14px;
  border-radius: 20px;     /* Pill shape */
  padding-left: 0;         /* Icon sits on edge */
  
  i {
    background-color: #f35525; /* Orange icon */
    display: inline-block;
    width: 40px;
    height: 40px;
    line-height: 40px;
    border-radius: 50%;    /* Circle */
    margin-right: 10px;
  }
  
  /* Responsive overrides:
     768px: border-radius: 15px, padding: 5px, icon: 30px
  */
}

/* Responsive item spacing:
   1200px: padding: 5px, height: 70px, line-height: 70px
   992px:  padding: 8px, height: 60px, line-height: 60px
   768px:  flex: 1 1 auto, min-width: 80px, height: 50px, text-align: center
*/
```

### `.language-switcher` (Language Dropdown Container)
```css
display: flex;
align-items: center;
margin-left: 20px;         /* Desktop spacing from nav */
flex-shrink: 0;            /* Never shrink */

/* Responsive overrides:
   1400px: margin-left: 15px
   1200px: margin-left: 12px
   992px:  flex: 0 0 auto, margin-left: 8px, margin-top: 15px, order: 3
   768px:  order: 3, width: 100%, margin-left: 0, margin-top: 10px,
           padding-top: 10px, border-top: 1px solid #eee
*/

.lang-switcher {
  position: relative;       /* For absolute .lang-menu */
  
  .lang-current {           /* The button */
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 8px 12px;
    border: 1px solid #ddd;
    border-radius: 20px;    /* Pill shape */
    background: #f8f9fa;
    color: #333;
    cursor: pointer;
    font-size: 12px;
    font-weight: 600;
    white-space: nowrap;
    transition: all 0.2s ease;
    
    &:hover {
      background: #e9ecef;
      border-color: #999;
    }
    
    &:focus {
      outline: none;
      box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
    }
    
    img.flag {
      width: 16px;
      height: 16px;
      border-radius: 2px;
      object-fit: cover;
    }
    
    span.code {
      font-weight: 700;
      letter-spacing: 0.5px;
    }
    
    span.chev {
      font-size: 10px;
      opacity: 0.6;
      transition: transform 0.2s ease;
    }
  }
  
  &.open .lang-current span.chev {
    transform: rotate(180deg);  /* Rotate on open */
  }
  
  .lang-menu {
    position: absolute;
    right: 0;
    top: calc(100% + 4px);
    min-width: 160px;
    background: #fff;
    border: 1px solid #ddd;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    padding: 4px;
    display: none;
    z-index: 10000;
    
    &.show {
      display: block;
    }
    
    .lang-item {
      margin: 0;
      
      button {
        width: 100%;
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 8px 10px;
        background: transparent;
        border: 0;
        border-radius: 6px;
        cursor: pointer;
        font-size: 13px;
        color: #333;
        transition: background 0.15s ease;
        font-weight: 500;
        
        img.flag {
          width: 16px;
          height: 16px;
          border-radius: 2px;
          flex-shrink: 0;
        }
        
        span.label {
          flex: 1;
        }
        
        &:hover {
          background: #f0f0f0;
        }
        
        &:focus {
          outline: none;
          background: #e8e8e8;
        }
      }
    }
  }
}
```

### `.menu-trigger` (Hamburger Menu)
```css
cursor: pointer;
position: absolute;
top: 23px;                 /* Desktop positioning */
width: 32px;
height: 40px;
text-indent: -9999em;      /* Hide text */
z-index: 99;
right: 20px;
display: none;             /* Hidden by default */
flex-shrink: 0;

/* Shows on mobile at 768px */
@media (max-width: 768px) {
  display: block !important;
  top: 12px;
  right: 15px;
}

/* Hamburger lines created with span and ::before/::after */
span {
  display: block;
  position: absolute;
  width: 30px;
  height: 2px;
  background-color: #1e1e1e;
  top: 16px;
  
  &::before, &::after {
    content: "";
    display: block;
    position: absolute;
    width: 75%;
    height: 2px;
    background-color: #1e1e1e;
  }
  
  &::before {
    top: -10px;
    transform-origin: 33% 100%;
  }
  
  &::after {
    top: 10px;
    transform-origin: 33% 0;
  }
}

&.active {
  span {
    background-color: transparent;
    
    &::before {
      transform: translateY(6px) translateX(1px) rotate(45deg);
    }
    
    &::after {
      transform: translateY(-6px) translateX(1px) rotate(-45deg);
    }
  }
}
```

## Responsive Breakpoints Summary

| Breakpoint | Width | Purpose | Key Changes |
|-----------|-------|---------|------------|
| Desktop | 1400px+ | Large screens | Full spacing, 28px logo |
| Large | 1200-1400px | Desktops | Slightly reduced 24px logo |
| Tablet | 992-1200px | Tablets | Wrappable nav, 22px logo |
| Medium | 768-992px | Larger mobiles | Wrapped flex layout |
| Mobile | <768px | Phones | Column flex, full-width items |
| Legacy | 767px- | Old styles | Maintained for compatibility |

## Spacing Reference

### Margin/Padding by Breakpoint

**Top margin of nav list:**
- Desktop (1400px+): 30px
- Large (1200px): 15px  
- Tablet (992px): 15px
- Medium (768px): 0
- Mobile (<768px): 0

**Horizontal padding on nav items:**
- Desktop: 10px left + 10px right = 20px total
- Large (1200px): 5px left + 5px right = 10px total
- Tablet (992px): 8px left + 8px right = 16px total
- Mobile (768px): 5px left + 5px right = 10px total

**Font sizes:**
- Desktop nav link: 15px
- Large (1200px): 13px
- Tablet (992px): 12px
- Mobile (768px): 11px

**Link heights:**
- Desktop: 40px (inside 100px container)
- Large (1200px): 35px (inside 70px)
- Tablet (992px): 32px (inside 60px)
- Mobile (768px): 30px (inside 50px)
