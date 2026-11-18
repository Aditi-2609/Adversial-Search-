document.querySelectorAll(".nav a").forEach(link=>{
  if(location.pathname.endsWith(link.dataset.page)) link.classList.add("active");
});
const menu=document.querySelector(".mobile-menu");
if(menu) menu.addEventListener("click",()=>document.querySelector(".sidebar").classList.toggle("open"));

function enableInputPersistence(){
  const storageKey=`ai-simulator:draft:${location.pathname}`;
  const fields=[...document.querySelectorAll("input[id],select[id],textarea[id]")]
    .filter(field=>!["search","filter"].includes(field.id));
  const reportStorageError=error=>{
    console.error("Unable to save this page's form draft.",error);
    let notice=document.getElementById("persistenceNotice");
    if(!notice){
      notice=document.createElement("div");
      notice.id="persistenceNotice";
      document.querySelector(".main")?.prepend(notice);
    }
    notice.className="notice error";
    notice.textContent="This browser could not save your form draft. Submitted game states are still stored by the server.";
  };
  try{
    const saved=JSON.parse(localStorage.getItem(storageKey)||"{}");
    fields.forEach(field=>{
      if(Object.prototype.hasOwnProperty.call(saved,field.id)) field.value=saved[field.id];
    });
    const save=()=>{
      const values={};
      fields.forEach(field=>{values[field.id]=field.value});
      try{
        localStorage.setItem(storageKey,JSON.stringify(values));
      }catch(error){
        reportStorageError(error);
      }
    };
    fields.forEach(field=>{
      field.addEventListener("input",save);
      field.addEventListener("change",save);
    });
  }catch(error){
    console.error("Unable to restore or save this page's form draft.",error);
    const notice=document.createElement("div");
    notice.className="notice error";
    notice.textContent="This browser could not save your form draft. Submitted game states are still stored by the server.";
    document.querySelector(".main")?.prepend(notice);
  }
}
enableInputPersistence();

function showNotice(id,message,type=""){
  const el=document.getElementById(id);
  if(!el)return;
  el.textContent=message;el.className="notice "+type;el.classList.remove("hidden");
}
function formatNumber(value,digits=2){
  const n=Number(value);return Number.isFinite(n)?n.toFixed(digits):"0";
}
