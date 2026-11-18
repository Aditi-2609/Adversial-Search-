let board=Array(9).fill(""),human="X",ai="O",gameOver=false,isThinking=false;
const boardEl=document.getElementById("board");
const aiTurnButton=document.getElementById("aiTurn");
const resetButton=document.getElementById("reset");
const tree=document.getElementById("tree");

function renderBoard(){
  boardEl.replaceChildren();
  board.forEach((value,index)=>{
    const cell=document.createElement("button");
    cell.type="button";
    cell.className=`cell ${value==="X"?"x":value==="O"?"o":""}`;
    cell.textContent=value;
    cell.setAttribute("aria-label",value?`Square ${index+1}: ${value}`:`Square ${index+1}: empty`);
    cell.disabled=Boolean(value)||gameOver||isThinking;
    cell.onclick=()=>humanMove(index);
    boardEl.appendChild(cell);
  });
}

function winner(cells){
  const lines=[[0,1,2],[3,4,5],[6,7,8],[0,3,6],[1,4,7],[2,5,8],[0,4,8],[2,4,6]];
  for(const [a,b,c] of lines)if(cells[a]&&cells[a]===cells[b]&&cells[a]===cells[c])return cells[a];
  return null;
}

async function humanMove(index){
  if(gameOver||isThinking||board[index])return;
  board[index]=human;
  renderBoard();
  if(checkGame())return;
  await runAi();
}

async function runAi(){
  if(gameOver||isThinking)return;
  isThinking=true;
  resetButton.disabled=true;
  aiTurnButton.disabled=true;
  renderBoard();
  showNotice("gameNotice","Calculating strategic move…");
  try{
    const {result,id}=await API.post("/api/adversarial/simulate",{
      board:board.slice(),
      depth:Number(document.getElementById("depth").value),
      algorithm:document.getElementById("algorithm").value,
      ai,human,name:"Tic-Tac-Toe"
    });
    if(result.move!==null)board[result.move]=ai;
    document.getElementById("best").textContent=result.move===null?"None":String(result.move+1);
    document.getElementById("nodes").textContent=result.nodes;
    document.getElementById("pruned").textContent=result.pruned;
    document.getElementById("time").textContent=`${result.execution_time_ms} ms`;
    renderEvaluatedMoves(result.evaluated_moves||[],result.move);
    renderBoard();
    const ended=checkGame();
    showNotice(
      "gameNotice",
      `${ended?"Game finished. ":"AI moved. "}Saved game state ${id}.`,
      ended?"success":""
    );
  }catch(error){
    showNotice("gameNotice",error.message,"error");
  }finally{
    isThinking=false;
    resetButton.disabled=false;
    aiTurnButton.disabled=gameOver;
    renderBoard();
  }
}

function renderEvaluatedMoves(moves,bestMove){
  tree.replaceChildren();
  if(!moves.length){
    tree.textContent="No legal moves were available.";
    return;
  }
  moves.forEach(({move,score})=>{
    const node=document.createElement("span");
    node.className=`tree-node${move===bestMove?" selected":""}`;
    node.textContent=`Square ${move+1}: ${score}`;
    node.title=move===bestMove?"Selected move":"Evaluated alternative";
    tree.appendChild(node);
  });
}

function checkGame(){
  const winningMarker=winner(board);
  if(winningMarker||board.every(Boolean)){
    gameOver=true;
    aiTurnButton.disabled=true;
    renderBoard();
    showNotice("gameNotice",winningMarker?`${winningMarker} wins!`:"Draw","success");
    return true;
  }
  return false;
}

resetButton.onclick=()=>{
  board=Array(9).fill("");
  gameOver=false;
  document.getElementById("best").textContent="—";
  document.getElementById("nodes").textContent="—";
  document.getElementById("pruned").textContent="—";
  document.getElementById("time").textContent="—";
  tree.textContent="Make a move or run the AI to evaluate legal moves.";
  showNotice("gameNotice","New game started.");
  aiTurnButton.disabled=false;
  renderBoard();
};
aiTurnButton.onclick=runAi;
renderBoard();
