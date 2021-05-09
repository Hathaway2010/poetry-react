import React from 'react';
import ReactDOM from 'react-dom'; 
import styles from './styles.scss';

const CTXT = JSON.parse(document.getElementById('ctxt').textContent);
/* Still to implement:
1. tooltips
2. own_poem
3. choose_poem on the page
4. rescan poem button
5. <3<3<3<3<3<3<3<3<3<3<3<3 
6. algorithm about
7. POEM GRAPHS EVENTUALLY MATPLOTLIB <3*/


function ScansionMenu(props) {
  const options = [];
  for (let alg in CTXT.scansions) {
    options.push(<option key={alg} value={alg}>{alg}</option>)
  }
  return (
    <div>
      <label htmlFor='algorithm'>Choose Base Scansion (undoes changes)</label>
      <select id='algorithm' name='algorithm' value={props.value} onChange={props.onChange}>
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

function PoemInterface(props) {
  const lines = [];
  for (let line in CTXT.poem.poem_dict) {
    lines.push(<Line key={`line${line}`} id={line} word_obj={CTXT.poem.poem_dict[line]} scan_obj={props.scansion[line]} onSymbolClick={props.onSymbolClick} onPClick={props.onPClick} onMClick={props.onMClick}/>)
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
      sCells.push(<ScanCell key={keyAndId} id={keyAndId} symbols={props.scan_obj[word]} onClick={props.onSymbolClick}/>)
    }
    const wCells = []
    for (let word in props.word_obj) {
      let keyAndId = `word${props.id}-${word}`
      wCells.push(<WordCell key={keyAndId} id={keyAndId} word={props.word_obj[word]} />)
    }
    const pmCells = []
    for (let word in props.word_obj) {
      let keyAndId = `pmc${props.id}-${word}`
      pmCells.push(<PlusMinusCell key={keyAndId} id={keyAndId} onPClick={props.onPClick} onMClick={props.onMClick}/>)
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
    symbols.push(<Symbol key={keyAndId} id={keyAndId} sym={props.symbols[i]} onClick={props.onClick} />)
  }
  return (
    <td id={props.id}>
      {symbols}
    </td>
  );
}

function Symbol(props) {
  return (
    <span className='symbol' id={props.id} onClick={props.onClick}>{props.sym}</span>
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
      <Plus onClick={props.onPClick} id={props.id} />
      <Minus onClick={props.onMClick} id={props.id} />
    </td>
  );

}

function Plus(props) {
  return (
    <button onClick={props.onClick} className='pm plus' id={`p${props.id}`}>+</button>
  );
}

function Minus(props) {
  return (
    <button onClick={props.onClick} className='pm minus' id={`m${props.id}`}>-</button>
  );
}

function SymbolTooltip(props) {
  return;
}

function PlusMinusTooltip(props) {
  return;
}

function SubmitButton(props) {
  return(
    <button id='submit-scansion' onClick={props.onSubmit}>Scan</button>
  );
}


class Scansion extends React.Component {
  constructor(props) {
    super(props);
    this.state = {startingAlgorithm: 'Blank Slate', currentScansion: CTXT.scansions['Blank Slate'].scansion, submitted: false};
    this.handleToggle = this.handleToggle.bind(this);
    this.handlePlus = this.handlePlus.bind(this);
    this.handleMinus = this.handleMinus.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
    this.handleSelect = this.handleSelect.bind(this);
  }
  handleSelect(e) {
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
        <ScansionMenu value={this.state.startingAlgorithm} onChange={this.handleSelect} />
        <div className="container">
          <PoemInterface scansion={this.state.currentScansion} onSubmit={this.handleSubmit} onSymbolClick={this.handleToggle} onPClick={this.handlePlus} onMClick={this.handleMinus}/>
          <Poem />
        </div>
      </div>
    )
  }
}

ReactDOM.render(
  <Scansion />, 
  document.getElementById('root')
);