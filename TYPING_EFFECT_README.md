# Typing Effect Animation

This typing effect adds a typewriter animation to text elements on your website.

## How to Use

### Basic Usage
Add the `data-typing-effect` attribute to any HTML element:

```html
<h2><span data-typing-effect>Your text here</span></h2>
```

### With Speed Control
Control the typing speed (milliseconds per character) using `data-typing-speed`:

```html
<h2><span data-typing-effect data-typing-speed="100">Slower typing</span></h2>
<h2><span data-typing-effect data-typing-speed="30">Faster typing</span></h2>
```

### With Delay
Add a delay before the animation starts using `data-typing-delay` (in milliseconds):

```html
<h2>
  <span data-typing-effect data-typing-speed="50">First line</span><br>
  <span data-typing-effect data-typing-speed="50" data-typing-delay="1000">Second line (starts after 1 second)</span>
</h2>
```

## Default Values

- **Speed**: 50 milliseconds per character
- **Delay**: 0 milliseconds (no delay)

## Files Used

- **CSS**: `/coralcity/static/newfront/assets/css/typing-effect.css`
- **JavaScript**: `/coralcity/static/newfront/assets/js/typing-effect.js`

Both files are already included in the `templates/newfrontend/base.html`

## Example Implementation

The first banner heading in `index.html` now uses the typing effect:

```html
<h2>
  <span data-typing-effect data-typing-speed="50">{% trans "Hurry!" %}</span><br>
  <span data-typing-effect data-typing-speed="50" data-typing-delay="1000">{% trans "Get the Best Villa for you" %}</span>
</h2>
```

This creates:
1. "Hurry!" types out immediately
2. After 1 second, "Get the Best Villa for you" types out on the next line
3. A blinking cursor appears during typing, then disappears when complete

## Browser Support

This effect works on all modern browsers that support:
- CSS animations
- JavaScript ES6 (arrow functions, template literals)
- data-* attributes
