export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const cors = {"Access-Control-Allow-Origin":"*","Access-Control-Allow-Headers":"Content-Type","Access-Control-Allow-Methods":"GET,POST,OPTIONS"};
    if (request.method === "OPTIONS") return new Response(null,{headers:cors});
    if (url.pathname === "/health") return Response.json({ok:true},{headers:cors});
    if (url.pathname === "/football-data") {
      const competition = url.searchParams.get("competition") || "WC";
      const season = url.searchParams.get("season") || "2026";
      const api = `https://api.football-data.org/v4/competitions/${competition}/matches?season=${season}`;
      const r = await fetch(api,{headers:{"X-Auth-Token":env.FOOTBALL_DATA_KEY}});
      return new Response(await r.text(),{status:r.status,headers:{...cors,"content-type":"application/json"}});
    }
    if (url.pathname === "/odds") {
      const sport = url.searchParams.get("sport") || "soccer_fifa_world_cup";
      const region = url.searchParams.get("region") || "eu";
      const api = `https://api.the-odds-api.com/v4/sports/${sport}/odds/?apiKey=${env.ODDS_API_KEY}&regions=${region}&markets=h2h,totals&oddsFormat=decimal&dateFormat=iso`;
      const r = await fetch(api);
      return new Response(await r.text(),{status:r.status,headers:{...cors,"content-type":"application/json"}});
    }
    return Response.json({error:"not found"},{status:404,headers:cors});
  }
}