const fs=require('fs'),http=require('http'),path=require('path');
const phase=process.argv[2];if(!['baseline','candidate'].includes(phase))throw Error('phase');
const root='/work/'+phase+'/web/dist';const evidence='/evidence';
const params={outputs:{json:{type:'Array<object>',value:[]}},vlm:{llm_id:'',system_prompt:''},enable_vision_enhancement:false,setups:[{fileFormat:'pdf',parse_method:'Docling',preprocess:'main_content',remove_toc:true,remove_header_footer:true,pages:[{from:1,to:100000}]}]};
let state={id:'pdf-cleanup-proof',title:phase+' PDF cleanup - local HTTP fixture',tenant_id:'fixture-owner',user_id:'fixture-owner',permission:'me',canvas_category:'dataflow_canvas',dsl:{globals:{},variables:[],retrieval:[],history:[],path:[],graph:{nodes:[{id:'File',type:'beginNode',position:{x:50,y:200},data:{label:'File',name:'File'},sourcePosition:'left',targetPosition:'right'},{id:'Parser:receipt',type:'parserNode',position:{x:350,y:200},data:{label:'Parser',name:'Parser',form:params},sourcePosition:'right',targetPosition:'left'}],edges:[{id:'file-parser',source:'File',sourceHandle:'start',target:'Parser:receipt',targetHandle:'end'}]},components:{File:{obj:{component_name:'File',params:{}},upstream:[],downstream:['Parser:receipt']},'Parser:receipt':{obj:{component_name:'Parser',params},upstream:['File'],downstream:[]}}}};
const statePath=evidence+'/exact-lf-'+phase+'-http-state.json';fs.writeFileSync(statePath,JSON.stringify(state,null,2));
const Model={model_id:'tenant-ocr-model',name:'Receipt OCR',provider_name:'PaddleOCR',provider_id:'provider',instance_name:'Local fixture',instance_id:'instance',model_type:['ocr'],status:'active',instance_status:'active'};
function log(row){fs.appendFileSync(evidence+'/exact-lf-'+phase+'-http-receipts.jsonl',JSON.stringify({time:new Date().toISOString(),...row})+'\n')}
http.createServer(async(req,res)=>{try{const url=new URL(req.url,'http://localhost');const chunks=[];for await(const c of req)chunks.push(c);const raw=Buffer.concat(chunks).toString();let body=raw;try{body=raw?JSON.parse(raw):null}catch{}
 const json=data=>{const out=JSON.stringify({code:0,message:'success',data});res.writeHead(200,{'Content-Type':'application/json','Content-Length':Buffer.byteLength(out)});res.end(out)};
 if(url.pathname.startsWith('/api/')||url.pathname.startsWith('/v1/')){
  log({method:req.method,path:req.url,body});
  if(url.pathname==='/api/v1/agents/pdf-cleanup-proof'){
   if(req.method!=='GET'){let next=body;if(typeof next.dsl==='string')next={...next,dsl:JSON.parse(next.dsl)};state={...state,...next};fs.writeFileSync(statePath,JSON.stringify(state,null,2))}return json(state)
  }
  if(url.pathname==='/api/v1/models')return json([Model]);
  if(url.pathname==='/api/v1/models/default'||url.pathname==='/api/v1/users/me/models')return json({llm_id:'',embd_id:'',img2txt_id:'',asr_id:'',tts_id:''});
  if(url.pathname==='/api/v1/users/me')return json({id:'fixture-owner',nickname:'Local fixture',email:'fixture@example.invalid',avatar:'',language:'English',theme:'light'});
  if(url.pathname.includes('/versions'))return json([]);
  if(url.pathname==='/api/v1/tenants')return json([{tenant_id:'fixture-owner',id:'fixture-owner',name:'Local fixture',role:'owner'}]);
  if(url.pathname==='/api/v1/agents')return json({agents:[state],total:1});
  return json([])
 }
 if(url.pathname==='/__proof/state'){res.writeHead(200,{'Content-Type':'application/json'});return res.end(JSON.stringify(state))}
 let file=path.join(root,decodeURIComponent(url.pathname));if(!file.startsWith(root))throw Error('invalid path');if(!fs.existsSync(file)||fs.statSync(file).isDirectory())file=root+'/index.html';const ext=path.extname(file);const mime={'.html':'text/html','.js':'text/javascript','.css':'text/css','.json':'application/json','.svg':'image/svg+xml','.png':'image/png','.ico':'image/x-icon','.woff2':'font/woff2','.wasm':'application/wasm'}[ext]||'application/octet-stream';res.writeHead(200,{'Content-Type':mime});fs.createReadStream(file).pipe(res);
}catch(e){log({error:String(e)});res.writeHead(500);res.end(String(e))}}).listen(19021,'0.0.0.0',()=>{fs.writeFileSync(evidence+'/exact-lf-'+phase+'-page-server.pid',String(process.pid));console.log(phase,'production Vite dist + synthetic local API fixture on19021')});
