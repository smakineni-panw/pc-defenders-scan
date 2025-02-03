from pcpi import session_loader
import csv
import json



if __name__ == '__main__':
    session_managers = session_loader.load_config()
    session = session_managers[0].create_cwp_session()

    cloud_limit = 50 #10
    services_limit = 50 #20
    assets_limit = 50 #8

    #GET ALL CLOUD ACCOUNTS
    cloud_accounts = []
    cloud_offset = 0
    while True:
        res = session.request('GET', f'/api/v1/cloud-scan-rules?project=Central+Console&offset={cloud_offset}&limit={cloud_limit}')
        if res.json():
            cloud_accounts.extend(res.json())
        else:
            break

        cloud_offset += cloud_limit

        if len(res.json()) < cloud_limit:
            break

    with open('out.csv', 'w') as outfile:
        # account_id, region, service_type, asset_name, last_modified, defended
        headers = ['Account ID', 'Region', 'Service Type', 'Asset Name', 'Last Modified', 'Defended']
        writer = csv.writer(outfile)

        writer.writerow(headers)

        #LOOP OVER ALL CLOUD ACCOUNTS
        for account in cloud_accounts:
            account_id = account['credentialId']

            services = []
            services_offset = 0
            while True:
                res = session.request('GET', f'/api/v1/cloud/discovery?offset={services_offset}&limit={services_limit}&credentialID={account_id}')
                if res.json():
                    services.extend(res.json())
                else:
                    break

                services_offset += services_limit

                if len(res.json()) < services_limit:
                    break
            
            #LOOP OVER ALL SERVICES
            for service in services:
                service_type = service['serviceType']
                region = service.get('region')

                assets = []
                assets_offset = 0

                while True:
                    url = ''
                    if region:
                        url = f'/api/v1/cloud/discovery/entities?accountIDs={account_id}&limit={assets_limit}&offset={assets_offset}&region={region}&reverse=false&serviceType={service_type}&sort=defended'
                    else:
                        url = f'/api/v1/cloud/discovery/entities?accountIDs={account_id}&limit={assets_limit}&offset={assets_offset}&reverse=false&serviceType={service_type}&sort=defended'
                    res = session.request('GET', url)
                    if res.json():
                        assets.extend(res.json())
                    else:
                        break

                    assets_offset += assets_limit

                    if len(res.json()) < assets_limit:
                        break

                #LOOP OVER ALL ASSETS AND SAVE TO FILE
        
                for asset in assets:
                    asset_name = asset['name']
                    # try:
                    #     asset_arn = asset['arn']
                    # except:
                    #     print(json.dumps(asset, indent=2))
                    last_modified = asset['lastModified']
                    defended = asset['defended']
                    writer.writerow([account_id, region, service_type, asset_name, last_modified, defended])

            






