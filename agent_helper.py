import requests
import json

def ask_agent(prompt: str)-> str:
    with open("apikey", "r") as f:
        API_KEY = f.read().strip()
    response = requests.post(
    url="https://openrouter.ai/api/v1/chat/completions",
    headers={
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        # "HTTP-Referer": "<YOUR_SITE_URL>", # Optional. Site URL for rankings on openrouter.ai.
        # "X-Title": "<YOUR_SITE_NAME>", # Optional. Site title for rankings on openrouter.ai.
    },
    data=json.dumps({
        "model": "tngtech/deepseek-r1t2-chimera:free",
        "messages": [
            {
            "role": "user",
            "content": prompt
            }
        ]
    })
    )
    result = parse_response(response.json()["choices"][0]["message"]["content"])
    return result

def parse_response(response: str) -> dict:
    """
    example response:
    <damain1>: <defensive_domain1>, <defensive_domain2>, ...
    <domain2>: <defensive_domain1>, <defensive_domain2>, ...
    """
    result = {}
    lines = response.splitlines()
    for line in lines:
        if ':' in line:
            company_domain, defensive_domains_str = line.split(':', 1)
            defensive_domains = [d.strip() for d in defensive_domains_str.split(',') if d.strip()]
            result[company_domain.strip()] = defensive_domains
    return result

if __name__ == "__main__":
    prompt = f"""
    Given the following registered domain names:\n 
    0amazon.com.	172800	in	ns	ns1.amzndns.co.uk.
0americanexpress.com.	172800	in	ns	dns1.cscdns.net.
0apple.com.	172800	in	ns	ns1.cafe24.co.kr.
0arrow.com.	172800	in	ns	pdns77.ultradns.biz.
0aypal.com.	172800	in	ns	ns1.redmonddc.com.
0brands.com.	172800	in	ns	ns45.domaincontrol.com.
0comcast.com.	172800	in	ns	dns101.comcast.net.
0delta.com.	172800	in	ns	nsg1.namebrightdns.com.
0farmers.com.	172800	in	ns	ns1.cafe24.co.kr.
0google.com.	172800	in	ns	ns1.parkingcrew.net.
0hertz.com.	172800	in	ns	ns1.brandshelter.com.
0hillips66.com.	172800	in	ns	dns1.cscdns.net.
0homedepot.com.	172800	in	ns	ns1.prncpm.com.
0huntington.com.	172800	in	ns	ns71.domaincontrol.com.
0intel.com.	172800	in	ns	desi.ns.cloudflare.com.
0mark.com.	172800	in	ns	coco.ns.cloudflare.com.
0mazon.com.	172800	in	ns	ns1.dns-parking.com.
0micron.com.	172800	in	ns	dns101.comcast.net.
0microsoft.com.	172800	in	ns	ns1.badgerdns.com.
0nalog.com.	172800	in	ns	dns1.yandex.net.
0neok.com.	172800	in	ns	ns0.phase8.net.
0netflix.com.	172800	in	ns	ns0.ukfast.net.
0oogle.com.	172800	in	ns	ns45.domaincontrol.com.
0oracle.com.	172800	in	ns	ns1.afternic.com.
0paypal.com.	172800	in	ns	ns-canada.topdns.com.
0pendoor.com.	172800	in	ns	nsg1.namebrightdns.com.
0phillips66.com.	172800	in	ns	dns1.cscdns.net.
0pple.com.	172800	in	ns	ns11.xincache.com.
0progressive.com.	172800	in	ns	ns1.hastydns.com.
0questdiagnostics.com.	172800	in	ns	dns1.registrar-servers.com.
0racle.com.	172800	in	ns	domain-for-sale.hugedomainsdns.com.
0reillyauto.com.	172800	in	ns	ns1.hastydns.com.
0rogressive.com.	172800	in	ns	3860.ns1.abovedomains.com.
0shkoshcorp.com.	172800	in	ns	ns-cloud-e1.googledomains.com.
0statefarm.com.	172800	in	ns	ns1.markmonitor.com.
0tesla.com.	172800	in	ns	a.share-dns.com.
0verizon.com.	172800	in	ns	ns1.clksite.com.
0vintiv.com.	172800	in	ns	ns1.ovintiv.com.
0walmart.com.	172800	in	ns	pns21.cloudns.net.
0wayfair.com.	172800	in	ns	ns1.redfoxdns.com.
0wenscorning.com.	172800	in	ns	ns1.abovedomains.com.
13harris.com.	172800	in	ns	ns0.dnsmadeeasy.com.
1abbott.com.	172800	in	ns	ns11.abovedomains.com.
1abcorp.com.	172800	in	ns	ns07.domaincontrol.com.
1airbnb.com.	172800	in	ns	expired1.maff.com.
1allstate.com.	172800	in	ns	ns53.domaincontrol.com.
1almart.com.	172800	in	ns	ns1.bodis.com.
1amazon.com.	172800	in	ns	ns1.markmonitor.com.
1americanexpress.com.	172800	in	ns	dns1.cscdns.net.
1analog.com.	172800	in	ns	ns-cloud-e1.googledomains.com.
    \n\nFor each of the following company domains: \n
    advanceautoparts.com
alaskaair.com
allstate.com
americanexpress.com
bankofamerica.com
capitalone.com
centerpointenergy.com
citizensbank.com
corning.com
dominionenergy.com
google.com
guardianlife.com
halliburton.com
homedepot.com
kohls.com
libertymutual.com
microsoft.com
modernatx.com
netflix.com
oracle.com
pfizer.com
target.com
thehartford.com
tractorsupply.com
verizon.com
wayfair.com
wellsfargo.com
\n
    , identify any registered defensive domains that are similar to the company domain. Notice that not all the registered defensive domains are for the above companies. Format your entire response in JSON format as a dictionary where keys are company domains and values are lists of similar registered defensive domains. No explanation.\n\n
    """
    
    res = ask_agent(prompt)
    print(res)