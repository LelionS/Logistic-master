const textBlocks = [
    "Where Logistics Meets Innovation",
    "Your Logistics Partner, Always"
];

const typingElement = document.getElementById('typing-text');
let currentTextIndex = 0;

function typeWriter(text, i) {
    if (i < text.length) {
        typingElement.innerHTML += text.charAt(i);
        i++;
        setTimeout(function() {
            typeWriter(text, i);
        }, 50); // Faster typing speed (adjust as needed)
    } else {
        setTimeout(function() {
            deleteText();
        }, 500); // Shorter delay before deleting (adjust as needed)
    }
}

function deleteText() {
    if (typingElement.innerHTML.length > 0) {
        typingElement.innerHTML = typingElement.innerHTML.slice(0, -1);
        setTimeout(function() {
            deleteText();
        }, 25); // Faster deleting speed (adjust as needed)
    } else {
        currentTextIndex = (currentTextIndex + 1) % textBlocks.length;
        setTimeout(function() {
            typeWriter(textBlocks[currentTextIndex], 0);
        }, 250); // Shorter delay before starting next text (adjust as needed)
    }
}

// Start typing effect
typeWriter(textBlocks[currentTextIndex], 0);