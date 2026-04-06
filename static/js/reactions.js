document.addEventListener('DOMContentLoaded', function() {
    initReactions();
});

function initReactions() {
    document.querySelectorAll('.reaction-btn').forEach(btn => {
        btn.addEventListener('click', async function(e) {
            e.preventDefault();
            
            const postId = this.dataset.postId;
            const reactionType = this.dataset.reaction;
            
            if (!postId || !reactionType) return;

            try {
                const response = await fetch(`/api/react/${postId}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ reaction_type: reactionType })
                });

                if (response.ok) {
                    const data = await response.json();
                    updateReactionButtons(postId, data.reactions, reactionType, data.action);
                } else if (response.status === 401) {
                    window.location.href = '/login';
                }
            } catch (error) {
                console.error('Reaction error:', error);
            }
        });
    });
}

function updateReactionButtons(postId, reactions, clickedReaction, action) {
    const container = document.querySelector(`[data-post-reactions="${postId}"]`);
    if (!container) return;

    container.querySelectorAll('.reaction-btn').forEach(btn => {
        const type = btn.dataset.reaction;
        const countSpan = btn.querySelector('.reaction-count');
        
        btn.classList.remove('active');
        
        if (type === clickedReaction && (action === 'added' || action === 'changed')) {
            btn.classList.add('active');
        }

        if (countSpan && reactions[type] !== undefined) {
            countSpan.textContent = reactions[type] || '';
        } else if (countSpan) {
            countSpan.textContent = '';
        }
    });

    const clickedBtn = container.querySelector(`[data-reaction="${clickedReaction}"]`);
    if (clickedBtn && (action === 'added' || action === 'changed')) {
        clickedBtn.classList.add('pulse');
        setTimeout(() => clickedBtn.classList.remove('pulse'), 300);
    }
}

const style = document.createElement('style');
style.textContent = `
    .reaction-btn.pulse {
        animation: pulse 0.3s ease;
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.2); }
        100% { transform: scale(1); }
    }
`;
document.head.appendChild(style);