/**
 * Typing Effect Animation
 * Animates text with a typewriter effect that can repeat
 */

class TypingEffect {
  constructor(element, options = {}) {
    this.element = element;
    this.fullText = element.textContent;
    this.speed = options.speed || 50; // milliseconds per character
    this.delay = options.delay || 0; // delay before starting
    this.deleteSpeed = options.deleteSpeed || 30; // milliseconds per character when deleting
    this.repeat = options.repeat !== false; // repeat by default
    this.repeatDelay = options.repeatDelay || 2000; // delay before repeating (ms)
    this.currentIndex = 0;
    this.isDeleting = false;
    this.isComplete = false;
    
    // Clear the element and prepare for animation
    element.textContent = '';
    element.classList.add('typing-effect');
    
    // Start the animation after delay
    if (this.delay > 0) {
      setTimeout(() => this.animate(), this.delay);
    } else {
      this.animate();
    }
  }
  
  animate() {
    if (!this.isDeleting) {
      // Typing phase
      if (this.currentIndex < this.fullText.length) {
        this.element.textContent += this.fullText.charAt(this.currentIndex);
        this.currentIndex++;
        setTimeout(() => this.animate(), this.speed);
      } else {
        // Typed complete
        this.isComplete = true;
        this.element.classList.add('complete');
        
        if (this.repeat) {
          // Wait before deleting
          setTimeout(() => {
            this.isDeleting = true;
            this.element.classList.remove('complete');
            this.animate();
          }, this.repeatDelay);
        }
      }
    } else {
      // Deleting phase
      if (this.currentIndex > 0) {
        this.element.textContent = this.fullText.substring(0, this.currentIndex - 1);
        this.currentIndex--;
        setTimeout(() => this.animate(), this.deleteSpeed);
      } else {
        // Deletion complete, restart typing
        this.isDeleting = false;
        this.currentIndex = 0;
        this.isComplete = false;
        setTimeout(() => this.animate(), 500);
      }
    }
  }
}

// Initialize typing effects when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
  // Find all elements with the typing-effect-trigger class
  const typingElements = document.querySelectorAll('[data-typing-effect]');
  
  typingElements.forEach(element => {
    const speed = element.dataset.typingSpeed || 50;
    const delay = element.dataset.typingDelay || 0;
    const deleteSpeed = element.dataset.typingDeleteSpeed || 30;
    const repeatDelay = element.dataset.typingRepeatDelay || 2000;
    const repeat = element.dataset.typingRepeat !== 'false'; // defaults to true
    
    new TypingEffect(element, {
      speed: parseInt(speed),
      delay: parseInt(delay),
      deleteSpeed: parseInt(deleteSpeed),
      repeatDelay: parseInt(repeatDelay),
      repeat: repeat
    });
  });
});
