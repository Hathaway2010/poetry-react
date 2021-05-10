import React from 'react';
import ReactDOM from 'react-dom'; 
import styles from './styles.scss';

const CTXT = JSON.parse(document.getElementById('ctxt').textContent);
/* Still to implement:
2. own_poem
3. choose_poem on the page
4. rescan poem button
5. <3<3<3<3<3<3<3<3<3<3<3<3 
7. POEM GRAPHS EVENTUALLY MATPLOTLIB <3*/

function PoetMenu(props) {
  const options = [];
  for (let i = 0; i < CTXT.poets.length; i++) {
    let p = CTXT.poets[i];
    options.push(<option key={p} value={p}>{p}</option>)  
  }
  return (
    <div>
      <label htmlFor="poet-menu">Choose a poet:</label>
      <select id="poet-menu" value={props.value} onChange={props.onChange}>
        {options}
      </select>
    </div>
  );
}

function PoemMenu(props) {
  const options = [];
  for (let i =0; i < props.options.human_scanned.length; i++) {
    let p = props.options.human_scanned[i];
    options.push(<option key={p[0]} value={p[0]}>{p[1]}</option>);
  }
  if (document.getElementById('promoted').textContent == 'Promoted: True') {
    for (let i = 0; i < props.options.computer_scanned.length; i++) {
      let p = props.options.computer_scanned[i];
      options.push(<option key={`poem${p[0]}`} value={p[0]}>{p[1]}</option>);
    }
  }
  return (
    <div>
      <label htmlFor="poem-menu">Choose a poem:</label>
      <select id="poem-menu" value={props.value} onChange={props.onChange}>
        {options}
      </select>
    </div>
  );
}

function NewPoemButton(props) {
  return (
    <div>
      <label htmlFor="submit-poem-choice">Go to new poem:</label>
      <button id="submit-poem-choice" onClick={props.onClick}>Go</button>
    </div>
  );
}

function ScansionMenu(props) {
  const options = [];
  for (let alg in CTXT.scansions) {
    options.push(<option key={alg} value={alg}>{alg}</option>)
  }
  return (
    <div>
      <label htmlFor='algorithm'>Choose Base Scansion (undoes changes)</label>
      <select id='algorithm' value={props.value} onChange={props.onChange}>
        {options}
      </select>
    </div>
  );
}

function Poem() {
  return (
    <div id="original-poem">
      <h3>{CTXT.poem.title}</h3>
      <p>by {CTXT.poem.poet}</p>
      <pre id="poem-text">{CTXT.poem.poem}</pre>  
    </div>
  );
}

function AlgorithmAbout(props) {
  if (props.text) {
    return (
      <div id="about-algorithm">{props.text}</div>
    )
  } else {
    return null;
  }
}

function PoemInterface(props) {
  const lines = [];
  for (let line in CTXT.poem.poem_dict) {
    lines.push(<Line key={`line${line}`} id={line} showTooltip={props.showTooltip} hideTooltip={props.hideTooltip} word_obj={CTXT.poem.poem_dict[line]} scan_obj={props.scansion[line]} onSymbolClick={props.onSymbolClick} onPClick={props.onPClick} onMClick={props.onMClick}/>)
  }
  return (
    <div id='poem-to-scan'>
      {lines}
      <SubmitButton onSubmit={props.onSubmit} />
    </div>
  );
}

function Line(props) {
  if (!props.word_obj || !props.scan_obj) {
    return (
      <table id={`line${props.id}`} className='empty'>
        <tbody>
          <tr></tr>
          <tr></tr>
        </tbody>
      </table>
    );
  } else {
    const sCells = []
    for (let word in props.word_obj) {
      let keyAndId = `scansion${props.id}-${word}`
      sCells.push(<ScanCell key={keyAndId} id={keyAndId} showTooltip={props.showTooltip} hideTooltip={props.hideTooltip} symbols={props.scan_obj[word]} onClick={props.onSymbolClick}/>)
    }
    const wCells = []
    for (let word in props.word_obj) {
      let keyAndId = `word${props.id}-${word}`
      wCells.push(<WordCell key={keyAndId} id={keyAndId} word={props.word_obj[word]} />)
    }
    const pmCells = []
    for (let word in props.word_obj) {
      let keyAndId = `pmc${props.id}-${word}`
      pmCells.push(<PlusMinusCell key={keyAndId} id={keyAndId} showTooltip={props.showTooltip} hideTooltip={props.hideTooltip} onPClick={props.onPClick} onMClick={props.onMClick}/>)
    }
    return (
      <table id={`line${props.id}`}>
        <tbody>
          <tr className="stress-row">{sCells}</tr>
          <tr className="word-row">{wCells}</tr>
          <tr className="plus-minus-row">{pmCells}</tr>
        </tbody>
      </table>
    );
  }
}

function ScanCell(props) {
  const symbols = []
  for (let i = 0; i < props.symbols.length; i++) {
    let keyAndId = `${props.id}-${i}`
    symbols.push(<Symbol key={keyAndId} id={keyAndId} showTooltip={props.showTooltip} hideTooltip={props.hideTooltip} sym={props.symbols[i]} onClick={props.onClick} />)
  }
  return (
    <td id={props.id}>
      {symbols}
    </td>
  );
}

function Symbol(props) {
  return (
    <span className='symbol' id={props.id} onMouseEnter={props.showTooltip} onMouseLeave={props.hideTooltip} onClick={props.onClick}>{props.sym}</span>
  );
}

function WordCell(props) {
  return (
    <td id={props.id}>
      {props.word}
    </td>
  );
}

function PlusMinusCell(props) {
  return (
    <td id={props.id} className='pmc'>
      <Plus onClick={props.onPClick} showTooltip={props.showTooltip} hideTooltip={props.hideTooltip} id={props.id} />
      <Minus onClick={props.onMClick} showTooltip={props.showTooltip} hideTooltip={props.hideTooltip} id={props.id} />
    </td>
  );

}

function Plus(props) {
  return (
    <button onClick={props.onClick} onMouseEnter={props.showTooltip} onMouseLeave={props.hideTooltip} className='pm plus' id={`p${props.id}`}>+</button>
  );
}

function Minus(props) {
  return (
    <button onClick={props.onClick} onMouseEnter={props.showTooltip} onMouseLeave={props.hideTooltip} className='pm minus' id={`m${props.id}`}>-</button>
  );
}

function SymbolTooltip(props) {
  return (
    <div className="tooltip" id="sctooltip">The "u" symbol means an unstressed syllable. "/" means a stressed syllable. Click to switch between symbols.</div>
  )
}
function PlusMinusTooltip(props) {
  return (
    <div className="tooltip" id="pmtooltip">The plus button adds a syllable. The minus removes one.</div>
  )
}

function SubmitButton(props) {
  return(
    <button id='submit-scansion' onClick={props.onSubmit}>Scan</button>
  );
}


class Scansion extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      startingAlgorithm: 'Blank Slate', 
      currentScansion: CTXT.scansions['Blank Slate'].scansion, 
      submitted: false, 
      selectedPoet: CTXT.poem.poet, 
      selectedPoem: CTXT.poem.title,
      poemObj: CTXT.poems
    };
    this.handleTooltipMouseover = this.handleTooltipMouseover.bind(this);
    this.handleTooltipMouseleave = this.handleTooltipMouseleave.bind(this);
    this.handleSelectPoet = this.handleSelectPoet.bind(this);
    this.handleSelectPoem = this.handleSelectPoem.bind(this);
    this.handleNewPoem = this.handleNewPoem.bind(this);
    this.handleSelectScansion = this.handleSelectScansion.bind(this);
    this.handleToggle = this.handleToggle.bind(this);
    this.handlePlus = this.handlePlus.bind(this);
    this.handleMinus = this.handleMinus.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
  }
  handleTooltipMouseover(e) {
    const rect = e.target.getBoundingClientRect();
    const tX = rect.right + 50;
    const tY = rect.top + 10 + window.pageYOffset;
    let tooltip;
    if (e.target.className =="scansion" || e.target.className == "symbol") {
      tooltip = document.getElementById("sctooltip");
    } else {
      tooltip = document.getElementById("pmtooltip");
  }
    tooltip.style.left = `${tX}px`;
    tooltip.style.top = `${tY}px`;
    tooltip.style.visibility = 'visible';
  }
  
  handleTooltipMouseleave() {
    const tooltips = document.querySelectorAll('.tooltip');
    tooltips.forEach(element => {
    element.style.visibility = 'hidden';
    });
  }
  handleSelectPoet(e) {
    const newPoet = e.target.value;
    fetch(`/choose_poem/${newPoet}`)
    .then(response => response.json())
    .then(data => {
      console.log(data);
      this.setState({selectedPoet: newPoet, poemObj: data})
    })
    this.setState({selectedPoet: newPoet});
  }

  handleSelectPoem(e) {
    const newPoem = e.target.value;
    this.setState({selectedPoem: newPoem});
  }

  handleNewPoem(e) {
    return;
  }

  handleSelectScansion(e) {
    const newScansion = e.target.value
    this.setState({startingAlgorithm: newScansion, currentScansion: CTXT.scansions[newScansion].scansion});
  }

  handleToggle(e) {
    const symbol_id = e.target.id;
    const [line, word, syll] = symbol_id.slice(8).split('-');
    const syll_idx = parseInt(syll, 10)
    this.setState(state => {
      const updating = JSON.parse(JSON.stringify(state.currentScansion));
      const w = updating[line][word];
      let newSym = 'u';
      if (w[syll_idx] === 'u') {
        newSym = '/';
      } 
      const newW = `${w.slice(0, syll_idx)}${newSym}${w.slice(syll_idx + 1)}`;
      updating[line][word] = newW;
      return ({
        currentScansion: updating
      });
    });
  }

  handlePlus(e) {
    const p_id = e.target.id;
    const [line, word] = p_id.slice(4).split('-');
    this.setState(state => {
      const updating = JSON.parse(JSON.stringify(state.currentScansion));
      const w = updating[line][word];
      const newW = `${w}u`;
      updating[line][word] = newW;
      return ({
        currentScansion: updating
      });
    });
  }

  handleMinus(e) {
    const m_id = e.target.id;
    const [line, word] = m_id.slice(4).split('-');
    this.setState(state => {
      const updating = JSON.parse(JSON.stringify(state.currentScansion));
      const w = updating[line][word];
      const newW = w.slice(0, w.length - 1);
      updating[line][word] = newW;
      return ({
        currentScansion: updating
      });
    });
  }

  handleSubmit() {
    function compareScansion(authoritative, submitted) {
      let wordCount = 0;
      const diffList = []
      for (let line in submitted) {
        if (line) {
          for (let word in submitted[line]) {
            let agrees = submitted[line][word] === authoritative[line][word];
            changeColors(line, word, agrees);
            if (!agrees) {
              diffList.push([line, word])
            }
            wordCount++;
          }
        }
      }
      return [diffList, Math.round(diffList.length * 100 / wordCount)];
    }

    function scoreScansion(percentage) {
      if (percentage <= 10) {
        return 1
      } else if (percentage <= 30) {
        return 0
      } else {
        return -1
      }
    }

    function makeCorrectAlert(userIsAuthenticated, userIsPromoted, submitted, percentage, score) {
      const SCORES = {'1': 'gained', '0': 'neither gained nor lost', '-1': 'lost'}
      if (userIsAuthenticated && userIsPromoted) {
        alert(`New stresses will be recorded, but this will take a moment; disagreements between you and previous scansion (${percentage}% of words) will be marked in red, agreements in green.`);
      } else if (userIsAuthenticated && !submitted) {
        alert(`You have ${SCORES[score.toString()]} a point! Look at the poem to see where your scansion differed (${percentage}% of words) from the most recent authoritative scansion.`);
      } else if (userIsAuthenticated || submitted) {
        alert(`You just submitted this poem, so your score won't/wouldn't change, but look at the poem to see where your scansion differed (${percentage}% of words) from the most recent authoritative scansion.`);
      } else {
        alert(`If you were logged in, you would have ${SCORES[score.toString()]} a point. Look at the poem to see where your scansion differed (${percentage}% of words) from the most recent authoritative scansion.`);
      }
    }
    
    function changeColors(lineNumber, wordNumber, agrees) {
      const PALERED = '#ffcccc'
      const PALEGREEN = '#99ffbb'
      const id = `scansion${lineNumber}-${wordNumber}`
      const cellToChange = document.getElementById(id);
      if (cellToChange && agrees) {
        cellToChange.style.backgroundColor = PALEGREEN;
      } else if (cellToChange) {
        cellToChange.style.backgroundColor = PALERED;
      }
    }

    function isAuthenticated() {
      const loginElem = document.querySelector('#login_link');
      return (!loginElem);
    }

    function isPromoted() {
      const promElem = document.querySelector('#promoted');
      return promElem && promElem.textContent === 'Promoted: True'
   }

    function submitScore(cookie, score) {
      fetch('/', {method: 'PUT', body: JSON.stringify({
        score: score
      }), headers: { "X-CSRFToken": cookie },
      })
      .then(response => response.json())
      .then(data => {
        const sc = document.getElementById('score');
        sc.innerText = data.score;
        const pr = document.getElementById('promoted');
        pr.innerText = `Promoted: ${data.promoted}`

      });
    }
    function submitScansion(cookie, submittedScansion, diffs) {
      fetch('/', {method: 'PUT', body: JSON.stringify({
        scansion: submittedScansion,
        id: CTXT.poem.id,
        diffs: diffs
      }), headers: { "X-CSRFToken": cookie },
      })
    }
    
    function getCookie() {
      let cookieValue = null;
      if (document.cookie && document.cookie !== '') {
          var cookies = document.cookie.split(';');
          for (var i = 0; i < cookies.length; i++) {
              var cookie = cookies[i].trim()
              // Does this cookie string begin with the name we want?
              if (cookie.substring(0, 'csrftoken'.length + 1) === ('csrftoken' + '=')) {
                  cookieValue = decodeURIComponent(cookie.substring('csrftoken'.length + 1));
                  break;
              }
          }
      }
      return cookieValue;
    }
    let best = CTXT.scansions['House Robber Scan'].scansion;
    if (CTXT.poem.authoritative) {
      best = CTXT.poem.authoritative;
    }
    
    this.setState(state => {
      const [diffs, percentage] = compareScansion(best, state.currentScansion);
      let score = scoreScansion(percentage);
      const au = isAuthenticated()
      const prom = isPromoted()
      console.log(`Logged in: ${au}, promoted ${prom}`)
      makeCorrectAlert(au, prom, state.submitted, percentage, score);
      const csrftoken = getCookie()
      if (au && prom) {
        submitScansion(csrftoken, state.currentScansion, diffs);
      } else if (au && !state.submitted) {
        submitScore(csrftoken, score);
      }
      return ({
        submitted: true
      });
    });
  }

  render() {
    return (
      <div>
        <SymbolTooltip />
        <PlusMinusTooltip />
        <div id="menus">
          <PoetMenu value={this.state.selectedPoet} onChange={this.handleSelectPoet}/>
          <PoemMenu value={this.state.selectedPoem} options={this.state.poemObj} onChange={this.handleSelectPoem} />
          <NewPoemButton onClick={this.handleNewPoem} />
          <ScansionMenu value={this.state.startingAlgorithm} onChange={this.handleSelectScansion} />
        </div>
        <div className="container">
          <PoemInterface scansion={this.state.currentScansion} onSubmit={this.handleSubmit} showTooltip={this.handleTooltipMouseover} hideTooltip={this.handleTooltipMouseleave} onSymbolClick={this.handleToggle} onPClick={this.handlePlus} onMClick={this.handleMinus}/>
          <div id="provided">
            <Poem />
            <AlgorithmAbout text={CTXT.scansions[this.state.startingAlgorithm].about_algorithm}/>
          </div>
        </div>
      </div>
    )
  }
}

ReactDOM.render(
  <Scansion />, 
  document.getElementById('root')
);