(function(){
  var form=document.getElementById("picker");
  if(!form) return;
  var out=document.getElementById("picker-results");
  var status=document.getElementById("picker-status");
  var data=[];
  function label(b){
    var bits=[];
    if(b.dogs==="yes"||b.dogs==="designated") bits.push("dogs");
    if(b.guard==="yes"||b.guard==="seasonal") bits.push("lifeguards");
    if(b.chair==="yes"||b.mat==="yes") bits.push("access help");
    if(b.shell==="yes") bits.push("shells mentioned");
    if(b.kids) bits.push("kids");
    return bits.join(", ")||"see the beach page";
  }
  function show(list){
    if(!list.length){out.innerHTML="";status.textContent="No beach in this set matches those filters. Widen one filter, or browse the region pages.";return;}
    status.textContent=list.length+" beach"+(list.length===1?"":"es")+" match. Open a page for the sourced details.";
    out.innerHTML=list.map(function(b){
      return '<li class="hit"><a href="/beaches/'+b.slug+'/"><strong>'+b.name+"</strong></a><p>"+b.place+", "+b.countyName+". "+label(b)+".</p></li>";
    }).join("");
  }
  function apply(){
    var g=form.region.value, d=form.dogs.value, u=form.guard.value, c=form.chair.value, s=form.shell.value, k=form.kids.value;
    show(data.filter(function(b){
      if(g&&b.region!==g) return false;
      if(d==="yes"&&b.dogs!=="yes"&&b.dogs!=="designated") return false;
      if(d==="no"&&b.dogs!=="no"&&b.dogs!=="service") return false;
      if(u==="yes"&&b.guard!=="yes"&&b.guard!=="seasonal") return false;
      if(u==="no"&&b.guard!=="no") return false;
      if(c==="yes"&&b.chair!=="yes"&&b.mat!=="yes") return false;
      if(s==="yes"&&b.shell!=="yes") return false;
      if(k==="yes"&&!b.kids) return false;
      return true;
    }));
  }
  fetch("/assets/beaches.json").then(function(r){return r.json();}).then(function(j){data=j;apply();}).catch(function(){status.textContent="The beach list did not load. Use the region links below.";});
  form.addEventListener("change",apply);
  form.addEventListener("submit",function(e){e.preventDefault();apply();});
})();
