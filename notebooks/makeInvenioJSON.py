    elif metadataType == 'invenio':
        #    
        # initialize invenio dictionary
        # 
        metadata_d = {
        "access": {
            "files": "public",
            "record": "public"
        },
        "files": {
            "enabled": True
        },
        "metadata": {}
        }
        metadata_d['metadata']['creators'] = []              # Add creators to metadata dictionary, initialize as empty list

        for p, person in enumerate(input_df.at[i, 'Authors, Primary'].split(';')):
            person = person.replace('Dr. ','')
            if ',' in person:
                toks = person.split(',')
            else:
                toks = person.split(' ,')

            if len(toks) < 2 or len(toks) > 4:
                continue

            family = toks[0].replace(',','') if ',' in person else toks[1]
            family = family.strip()

            given = " ".join(toks[1:]) if ',' in person else toks[0]
            given = given.strip()                                       # .replace(' ','+')

            metadata_d['metadata']['creators'].append({'person_or_org': {'familyName': family, 'givenName': given}, 'type': 'Personal'})

        if len(str(input_df.at[i, 'Abstract'])) > 0 and str(input_df.at[i, 'Abstract']) != 'nan':
            metadata_d['metadata']['description'] = input_df.at[i, 'Abstract']
        #
        # Create a unique identifier for each record using a combination of the iPlaces DOI prefix, the abbreviation for the class
        # (Biology and Geology of Tropical Islands), the publication year, the paper index, and creator names.
        # The creator names are concatenated together with underscores, and spaces and special characters are removed or 
        # replaced to ensure the identifier is valid.
        #
        identifier = f"{'_'.join([ x['person_or_org']['familyName'].replace(' ','')+'_'+ x['person_or_org']['givenName'].replace(' ','').replace('.','') for x in metadata_d['metadata']['creators'] ])}"
        identifier = identifier.replace('/','-').replace(':','-').replace('?','-').replace('"','-').replace('\'','-').replace(',','').replace('(','').replace(')','').replace('\n','_')
        identifier = f"{prefix}/bgtl/{str(input_df.at[i, 'Pub Year'])}/{paperIndex}/{identifier}"
        metadata_d['metadata']['identifiers'] = [{'identifier': identifier, 'scheme': 'doi'}]

        metadata_d['metadata']['publication_date']   = input_df.at[i, 'Pub Year']
        metadata_d['metadata']['publisher']          = 'University of California, Berkeley'
        metadata_d['metadata']['resource_type']      = 'publication-preprint'

        contributor_Gump = {                                        # define Gump as a contributor
            "person_or_org": {
                "name": "Gump South Pacific Research Station",
                "type": "Organizational",
                "identifiers": [{
                "scheme": "ror",
                "identifier": "04sk0et52"
                }],
            },
            "role": {"id": "Sponsor"},
            "affiliations": [{
                "id": "04sk0et52",
                "name": "Gump South Pacific Research Station",
            }]
        }
        metadata_d['metadata']['contributors']      = [contributor_Gump]

        if len(str(input_df.at[i, 'Keywords'])) > 0 and str(input_df.at[i, 'Keywords']) != 'nan':
            keywords_l = str(input_df.at[i, 'Keywords']).split(';')              # some keywords are delimited with ";"
            if len(keywords_l) == 1:
                keywords_l = str(input_df.at[i, 'Keywords']).split(',')          # some keywords are delimited with ","

            for subject in keywords_l:
                subject = subject.strip()
                if len(subject) > 0:
                    if 'subjects' not in metadata_d['metadata']:
                        metadata_d['metadata']['subjects'] = []
                    metadata_d['metadata']['subjects'].append({'subject': subject})
        #
        # The index spreadsheet includes a column named "organism" that includes fairly high-level organism keywords
        # The metadata includes an element named subjectScheme that identifies keywords of a specific type.
        # In this case that is set to "organism" to differentiate these keywords from the general set
        #  
        if all(['organism' in input_df.columns, 
                len(str(input_df.at[i, 'organism'])),
                str(input_df.at[i, 'organism']) != 'nan']):
            if 'subjects' not in metadata_d['metadata']:
                metadata_d['metadata']['subjects'] = []
            metadata_d['metadata']['subjects'].append({'subject': input_df.at[i, 'organism'], 'subjectScheme':'organism'})
        #
        # The index spreadsheet includes a column named "where" that includes fairly high-level location keywords
        # The metadata includes an element named subjectScheme that identifies keywords of a specific type.
        # In this case that is set to "where" to differentiate these keywords from the general set.
        #  
        if all(['where' in input_df.columns, 
                len(str(input_df.at[i, 'where'])),
                str(input_df.at[i, 'where']) != 'nan']):
            if 'subjects' not in metadata_d['metadata']:
                metadata_d['metadata']['subjects'] = []
            metadata_d['metadata']['subjects'].append({'subject': input_df.at[i, 'where'], 'subjectScheme':'where'})

        if len(str(input_df.at[i, 'Title Primary'])) > 0 and str(input_df.at[i, 'Title Primary']) != 'nan':
            metadata_d['metadata']['title'] = input_df.at[i, 'Title Primary']

        relatedIsPartOf = f"10.60950/bgtl/ProjectIdentifierForYear_{str(input_df.at[i, 'Pub Year'])}"
        metadata_d['metadata']['related_identifiers'] = [{'identifier': relatedIsPartOf, 
                                                        'relation_type': {'id': 'ispartof'},
                                                        'resource_type': {'id': 'other'},
                                                        'scheme': 'doi'}]

        metadata_d['metadata']['version'] = 1

#        fileName = f"{'_'.join([ x['person_or_org']['familyName'].replace(' ','')+'_'+ x['person_or_org']['givenName'].replace(' ','').replace('.','') for x in metadata_d['metadata']['creators'] ])}.json"
        fileName = identifier.replace('/','_')
        fileName = fileName.replace('/','-').replace(':','-').replace('?','-').replace('"','-').replace('\'','-').replace(',','').replace('(','').replace(')','').replace('\n','_')
        fileName = f'{str(metadata_d["data"]["metadata"]["publication_date"])}/{paperIndex}_' + fileName
