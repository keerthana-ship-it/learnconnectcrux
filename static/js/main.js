document.addEventListener('DOMContentLoaded', function() {
    // Enable Bootstrap tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Bookmark content functionality
    const bookmarkContentBtns = document.querySelectorAll('.bookmark-content-btn');
    bookmarkContentBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const contentId = this.getAttribute('data-content-id');
            
            fetch(`/collect/bookmark/${contentId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'added') {
                    this.innerHTML = '<i class="fas fa-bookmark"></i>';
                    this.classList.remove('btn-outline-primary');
                    this.classList.add('btn-primary');
                    this.setAttribute('title', 'Remove from bookmarks');
                } else {
                    this.innerHTML = '<i class="far fa-bookmark"></i>';
                    this.classList.remove('btn-primary');
                    this.classList.add('btn-outline-primary');
                    this.setAttribute('title', 'Add to bookmarks');
                }
                
                // Refresh tooltip
                var tooltip = bootstrap.Tooltip.getInstance(this);
                if (tooltip) {
                    tooltip.dispose();
                }
                new bootstrap.Tooltip(this);
            })
            .catch(error => {
                console.error('Error:', error);
            });
        });
    });

    // Bookmark event functionality
    const bookmarkEventBtns = document.querySelectorAll('.bookmark-event-btn');
    bookmarkEventBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const eventId = this.getAttribute('data-event-id');
            
            fetch(`/connect/bookmark/${eventId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'added') {
                    this.innerHTML = '<i class="fas fa-bookmark"></i>';
                    this.classList.remove('btn-outline-primary');
                    this.classList.add('btn-primary');
                    this.setAttribute('title', 'Remove from bookmarks');
                } else {
                    this.innerHTML = '<i class="far fa-bookmark"></i>';
                    this.classList.remove('btn-primary');
                    this.classList.add('btn-outline-primary');
                    this.setAttribute('title', 'Add to bookmarks');
                }
                
                // Refresh tooltip
                var tooltip = bootstrap.Tooltip.getInstance(this);
                if (tooltip) {
                    tooltip.dispose();
                }
                new bootstrap.Tooltip(this);
            })
            .catch(error => {
                console.error('Error:', error);
            });
        });
    });

    // Quiz functionality
    const quizForm = document.getElementById('quiz-form');
    if (quizForm) {
        const questionElements = document.querySelectorAll('.quiz-question');
        let currentQuestionIndex = 0;
        
        // Show only the first question initially
        if (questionElements.length > 0) {
            updateQuestionVisibility();
        }
        
        // Next question button clicks
        const nextButtons = document.querySelectorAll('.next-question');
        nextButtons.forEach(button => {
            button.addEventListener('click', function() {
                const questionId = this.getAttribute('data-question-id');
                const selectedOption = document.querySelector(`input[name="question_${questionId}"]:checked`);
                
                if (selectedOption) {
                    currentQuestionIndex++;
                    updateQuestionVisibility();
                    window.scrollTo(0, 0);
                } else {
                    alert('Please select an answer before proceeding.');
                }
            });
        });
        
        // Previous question button clicks
        const prevButtons = document.querySelectorAll('.prev-question');
        prevButtons.forEach(button => {
            button.addEventListener('click', function() {
                currentQuestionIndex--;
                updateQuestionVisibility();
                window.scrollTo(0, 0);
            });
        });
        
        // Function to update question visibility
        function updateQuestionVisibility() {
            questionElements.forEach((question, index) => {
                if (index === currentQuestionIndex) {
                    question.style.display = 'block';
                } else {
                    question.style.display = 'none';
                }
            });
            
            // Update progress bar if exists
            const progressBar = document.getElementById('quiz-progress');
            if (progressBar) {
                const progress = ((currentQuestionIndex + 1) / questionElements.length) * 100;
                progressBar.style.width = `${progress}%`;
                progressBar.setAttribute('aria-valuenow', progress);
            }
        }
    }
    
    // Filter dropdowns in content and events pages
    const filterForms = document.querySelectorAll('.filter-form');
    filterForms.forEach(form => {
        const filterInputs = form.querySelectorAll('select, input[type="checkbox"]');
        filterInputs.forEach(input => {
            input.addEventListener('change', function() {
                form.submit();
            });
        });
    });
    
    // Profile skills input tags
    const skillsInput = document.getElementById('skills');
    if (skillsInput) {
        let skills = skillsInput.value ? skillsInput.value.split(',') : [];
        refreshSkillTags();
        
        document.getElementById('add-skill').addEventListener('click', function() {
            const newSkill = document.getElementById('new-skill').value.trim();
            if (newSkill && !skills.includes(newSkill)) {
                skills.push(newSkill);
                skillsInput.value = skills.join(',');
                document.getElementById('new-skill').value = '';
                refreshSkillTags();
            }
        });
        
        function refreshSkillTags() {
            const tagsContainer = document.getElementById('skill-tags');
            tagsContainer.innerHTML = '';
            
            skills.forEach(skill => {
                if (skill.trim()) {
                    const tag = document.createElement('span');
                    tag.className = 'badge bg-primary me-2 mb-2';
                    tag.textContent = skill.trim();
                    
                    const removeBtn = document.createElement('button');
                    removeBtn.className = 'btn-close btn-close-white ms-1';
                    removeBtn.setAttribute('type', 'button');
                    removeBtn.setAttribute('aria-label', 'Remove');
                    removeBtn.style.fontSize = '0.5em';
                    
                    removeBtn.addEventListener('click', function() {
                        skills = skills.filter(s => s !== skill);
                        skillsInput.value = skills.join(',');
                        refreshSkillTags();
                    });
                    
                    tag.appendChild(removeBtn);
                    tagsContainer.appendChild(tag);
                }
            });
        }
    }
});
