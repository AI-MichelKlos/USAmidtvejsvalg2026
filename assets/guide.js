(() => {
  'use strict';

  const levelButtons = [...document.querySelectorAll('[data-level]')];
  const panels = [...document.querySelectorAll('[data-level-panel]')];
  function chooseLevel(level) {
    levelButtons.forEach(button => {
      const selected = button.dataset.level === level;
      button.classList.toggle('is-active', selected);
      button.setAttribute('aria-pressed', String(selected));
    });
    panels.forEach(panel => { panel.hidden = panel.dataset.levelPanel !== level; });
  }
  levelButtons.forEach(button => button.addEventListener('click', () => chooseLevel(button.dataset.level)));

  const lawSteps = [
    { title: 'Et lovforslag fremsættes', copy: 'Et medlem af Kongressen fremsætter et lovforslag i Huset eller Senatet. Forslag om føderale skatteindtægter skal begynde i Huset. Forslaget behandles normalt også i et udvalg.' },
    { title: 'Begge kamre skal vedtage samme tekst', copy: 'Repræsentanternes Hus og Senatet behandler lovforslaget. For at det kan sendes til præsidenten, skal begge kamre normalt have vedtaget præcis samme lovtekst.' },
    { title: 'Præsidenten tager stilling', copy: 'Præsidenten kan underskrive lovforslaget, så det bliver lov, eller nedlægge veto. Der findes også særlige regler, når præsidenten ikke handler inden for fristen.' },
    { title: 'Kongressen kan tilsidesætte et veto', copy: 'Hvis præsidenten nedlægger veto, kan Kongressen alligevel vedtage loven, hvis mindst to tredjedele stemmer for i både Repræsentanternes Hus og Senatet. Det er ikke en almindelig flertalsafgørelse.' }
  ];
  let lawIndex = 0;
  const lawButtons = [...document.querySelectorAll('[data-law-step]')];
  function renderLaw() {
    lawButtons.forEach((button, index) => {
      const active = index === lawIndex;
      button.classList.toggle('is-active', active);
      button.setAttribute('aria-pressed', String(active));
    });
    document.getElementById('law-index').textContent = String(lawIndex + 1).padStart(2, '0') + ' / 04';
    document.getElementById('law-detail-title').textContent = lawSteps[lawIndex].title;
    document.getElementById('law-detail-copy').textContent = lawSteps[lawIndex].copy;
    document.getElementById('law-prev').disabled = lawIndex === 0;
    document.getElementById('law-next').disabled = lawIndex === lawSteps.length - 1;
  }
  lawButtons.forEach((button, index) => button.addEventListener('click', () => { lawIndex = index; renderLaw(); }));
  document.getElementById('law-prev').addEventListener('click', () => { lawIndex = Math.max(0, lawIndex - 1); renderLaw(); });
  document.getElementById('law-next').addEventListener('click', () => { lawIndex = Math.min(lawSteps.length - 1, lawIndex + 1); renderLaw(); });
  renderLaw();

  const questions = [
    {
      text: 'Hvem er på valg ved det amerikanske midtvejsvalg i 2026?',
      options: ['Præsidenten og alle senatorer', 'Alle medlemmer af Repræsentanternes Hus og omkring en tredjedel af Senatet', 'Kun guvernørerne'],
      answer: 1,
      explanation: 'Alle 435 stemmeberettigede pladser i Huset er på valg hvert andet år. Omkring en tredjedel af Senatets pladser er på valg. Præsidenten er ikke på valg i 2026.'
    },
    {
      text: 'Kan amerikanske vælgere stemme om, hvem der skal være sheriff?',
      options: ['Ja, mange steder, men der findes undtagelser', 'Ja, i samtlige amerikanske kommuner', 'Nej, sheriffer udpeges altid af præsidenten'],
      answer: 0,
      explanation: 'I mange counties er sheriffen folkevalgt, men det gælder ikke alle steder, og sheriffer findes ikke i samme form overalt.'
    },
    {
      text: 'Kan amerikanere stemme om dommere?',
      options: ['Nej, det er forbudt i hele USA', 'Ja, alle føderale dommere er på valg hvert fjerde år', 'Ja, nogle delstatsdommere vælges, mens føderale dommere udnævnes'],
      answer: 2,
      explanation: 'Ordningen varierer mellem delstater. Nogle dommere vælges direkte, andre gennem bekræftelsesvalg eller ved udnævnelse. Føderale dommere vælges ikke ved folkeafstemning.'
    },
    {
      text: 'Hvad skal der normalt ske, før et føderalt lovforslag kan blive en lov?',
      options: ['Begge Kongressens kamre skal vedtage samme tekst, og lovforslaget går derefter til præsidenten', 'Senatet alene kan vedtage enhver lov', 'Præsidenten kan alene vedtage alle føderale love'],
      answer: 0,
      explanation: 'Lovgivningen skal normalt vedtages af både Huset og Senatet og sendes til præsidenten. Et veto kan i nogle tilfælde tilsidesættes af Kongressen.'
    },
    {
      text: 'Er det samme poster og spørgsmål, der er på stemmesedlen overalt i USA?',
      options: ['Ja, alle får præcis den samme stemmeseddel', 'Nej, den afhænger af delstat, county, by og valgår', 'Ja, men kun ved midtvejsvalg'],
      answer: 1,
      explanation: 'Lokale valglove, valgperioder og borgerens adresse bestemmer, hvilke embeder og afstemninger der står på stemmesedlen.'
    }
  ];
  let quizIndex = 0;
  let score = 0;
  let answered = false;
  const $ = id => document.getElementById(id);
  const choicesElement = $('quiz-choices');
  function renderQuiz() {
    const question = questions[quizIndex];
    answered = false;
    $('quiz-progress').textContent = 'Spørgsmål ' + (quizIndex + 1) + ' af ' + questions.length;
    $('quiz-score').textContent = score + ' rigtige';
    $('quiz-bar').style.width = ((quizIndex + 1) / questions.length * 100) + '%';
    $('quiz-question').textContent = question.text;
    $('quiz-feedback').hidden = true;
    $('quiz-next').hidden = true;
    $('quiz-restart').hidden = true;
    choicesElement.replaceChildren();
    question.options.forEach((option, i) => {
      const button = document.createElement('button');
      button.type = 'button';
      button.className = 'quiz-choice';
      button.textContent = option;
      button.addEventListener('click', () => answerQuestion(i));
      choicesElement.appendChild(button);
    });
  }
  function answerQuestion(index) {
    if (answered) return;
    answered = true;
    const question = questions[quizIndex];
    if (index === question.answer) score += 1;
    const buttons = [...choicesElement.querySelectorAll('button')];
    buttons.forEach((button, i) => {
      button.disabled = true;
      if (i === question.answer) button.classList.add('is-correct');
      else if (i === index) button.classList.add('is-wrong');
    });
    $('quiz-score').textContent = score + ' rigtige';
    $('quiz-feedback').textContent = (index === question.answer ? 'Rigtigt! ' : 'Ikke helt. ') + question.explanation;
    $('quiz-feedback').hidden = false;
    if (quizIndex === questions.length - 1) {
      $('quiz-restart').hidden = false;
      $('quiz-feedback').textContent += ' Du fik ' + score + ' af ' + questions.length + ' rigtige.';
    } else $('quiz-next').hidden = false;
  }
  $('quiz-next').addEventListener('click', () => {
    if (!answered || quizIndex >= questions.length - 1) return;
    quizIndex += 1;
    renderQuiz();
  });
  $('quiz-restart').addEventListener('click', () => {
    quizIndex = 0;
    score = 0;
    renderQuiz();
  });
  renderQuiz();
})();