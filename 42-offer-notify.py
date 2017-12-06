import sys, requests, os, pickle
from bs4 import BeautifulSoup as bs
from datetime import datetime, timedelta

base_url = 'https://companies.intra.42.fr'
offers_url = base_url + '/en/offers'
query_params = '?filter%5Bcontract_type%5D={contract_type}' + \
    '&filter%5Bexpertise_id%5D={expertise_id}' + \
    '&filter%5Bcampus_id%5D={campus_id}' + \
    '&filter%5Bcountry%5D={country}' + \
    '&rev_sort=&search='
save_file = os.path.join(os.environ.get('HOME'), '.42-offer-notify.pickle')

def get_old_data():
    try:
        with open(save_file, 'rb') as old_file:
            return pickle.load(old_file)
    except FileNotFoundError:
        return None

def save_data(data):
    with open(save_file, 'wb') as new_file:
        pickle.dump(data, new_file)

def get_page_offers(page):
    offers = page.find_all(class_='border-stage') or page.find_all(class_='border-emploi')
    processed = []
    for offer in offers:
        try:
            processed.append({
                'title': offer.find(class_='title-offer').get_text().strip(),
                'url': offer.find(class_='title-offer').find('a').get('href'),
                'description': offer.find(class_='description-offer').get_text().strip(),
                'date': offer.find(class_='data-short-date').get_text().strip(),
                'company': offer.find(class_='poste-info-bold').find('a').get_text().strip()
            })
        except Exception as e:
            print('ERROR: ' + str(e) + '\n' + str(offer))
    return processed

def new_offer(offer):
    print(offer)

def main(token):
    contracts = ['cdd_partiel', 'cdi_partiel', 'stage_partiel']
    old_data = get_old_data()
    data = {
        'time': datetime.now(),
        'contracts': {
        }
    }
    if old_data != None:
        if data['time'] - old_data['time'] < timedelta(hours=1):
            print('not enough time spent')
            return
    for contract in contracts:
        cookies = {
            '_intra_42_session_production': token,
        }
        url = offers_url + query_params.format(**{
            'contract_type': contract,
            'expertise_id': '',
            'campus_id': '',
            'country': '',
        })
        req = requests.get(url, cookies=cookies)
        page = bs(req.text, 'html.parser')
        offers = get_page_offers(page)
        data['contracts'][contract] = offers
    save_data(data)
    for contract, offers in data['contracts'].items():
        for offer in offers:
            try:
                old_offers = old_data['contracts'][contract]
                found = False
                for old_offer in old_contract:
                    if old_offer['url'] == offer['url']:
                        found = True
                        break
                if found:
                    continue
                else:
                    new_offer(offer)
            except:
                new_offer(offer)

if __name__ == '__main__':
    token = os.environ.get('SESSION_TOKEN_42')
    main(token)
