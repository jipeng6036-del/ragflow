async page => {
 await page.addInitScript(() => { localStorage.setItem('Authorization','Bearer local-synthetic-fixture');localStorage.setItem('token','local-synthetic-fixture');localStorage.setItem('userInfo',JSON.stringify({id:'fixture-owner',nickname:'Local fixture',email:'fixture@example.invalid'}));localStorage.setItem('lng','en'); });
 await page.goto('http://127.0.0.1:19021/agent/pdf-cleanup-proof?category=dataflow_canvas');
}
