integration_from_csv.py
import warnings
import pandas as pd


def drive_scan(in_dir, in_dir_file, out_dir, now_):

    list_df = pd.read_csv(in_dir_file, dtype={'Line': 'object', 'MouseID': 'object'})  # control; since they're added
    list_df['root'] = list_df['Line'] + list_df['MouseID'].apply(lambda x: f'_{x}')
    list_df = list_df.groupby(['root']).apply(lambda x: x)  # grouped by the root folder name
    list_df['rootUnique'] = ''  # to be valued in the following
    list_df['rootMulti'] = ''  # to be valued in the following
    list_df['parUnique'] = ''  # to be valued in the following
    list_df['parMulti'] = ''  # to be valued in the following
    list_df['uniqueExistence'] = ''

    is_similar = False  # default value to start with...
    index_list = list(list_df.index)
    for i in range(len(index_list)):
        root_ = list_df.at[index_list[i], 'root']
        date_ = list_df.at[index_list[i], 'Date']
        paradigm_ = list_df.at[index_list[i], 'Paradigm']
        print(f'({i+1}/{len(index_list)}): Searching for {root_}/{date_}_{paradigm_}...')
        # taking care of the first element's error
        try:
            is_similar = list_df.at[index_list[i-1], 'root'] == root_  # check similarity to avoid duplicate glob scan!
        except:
            pass
        # specific scan
        if not is_similar:
            # print('is NOT similar!!!')  # just a control check
            rglob_list = list(in_dir.rglob(root_))  # list of the generator | generator would be dead hereafter
            # primary check
            if not rglob_list:
                # nothing returned
                print(in_dir)
                print(in_dir_file)
                print(root_)
                warnings.warn(f'NO matching directory could be found for the following root-name (ignoring...): \n'
                              f'{root_}')
                is_found = False
                continue
            elif len(rglob_list) > 1:
                # not unique
                warnings.warn(f'MULTIPLE matching directories found for the following root-name (ignoring...): \n'
                              f'{root_}')
                is_found = False  # as good as NO found
                list_df.at[index_list[i], 'rootMulti'] = str(rglob_list)
                continue
            # if passed
            print(f'** found the root file for: {root_}')
            is_found = True
            list_df.at[index_list[i], 'rootUnique'] = str(rglob_list)
            # paradigm
            # date_ = list_df.at[index_list[i], 'Date']
            # paradigm_ = list_df.at[index_list[i], 'Paradigm']
            sub_rglob_list = list(rglob_list[0].glob(f'*{date_}_{paradigm_}'))
            # final check
            if not sub_rglob_list:
                # nothing returned
                warnings.warn(f'NO matching directory could be found for the following date_paradigm (ignoring...): \n'
                              f'{date_}_{paradigm_}')
                continue
            elif len(sub_rglob_list) > 1:
                # not unique
                warnings.warn(f'MULTIPLE matching directories found for the following date_paradigm (ignoring...): \n'
                              f'{date_}_{paradigm_}')
                list_df.at[index_list[i], 'parMulti'] = str(sub_rglob_list)
                continue
            # if passed:
            print(f'** and found the following date_paradigm: {date_}_{paradigm_}')
            list_df.at[index_list[i], 'parUnique'] = str(sub_rglob_list)
            list_df.at[index_list[i], 'uniqueExistence'] = True

        elif is_similar and is_found:
            # print('is similar and is found!!!')  # just a control check
            list_df.at[index_list[i], 'rootUnique'] = str(rglob_list)  # just to fill the cell
            # paradigm
            # date_ = list_df.at[index_list[i], 'Date']
            # paradigm_ = list_df.at[index_list[i], 'Paradigm']
            sub_rglob_list = list(rglob_list[0].glob(f'*{date_}_{paradigm_}'))  # uses the last found rglob_list
            # final check
            if not sub_rglob_list:
                # nothing returned
                warnings.warn(f'NO matching directory could be found for the following date_paradigm (ignoring...): \n'
                              f'{date_}_{paradigm_}')
                continue
            elif len(sub_rglob_list) > 1:
                # not unique
                warnings.warn(f'MULTIPLE matching directories found for the following date_paradigm (ignoring...): \n'
                              f'{date_}_{paradigm_}')
                list_df.at[index_list[i], 'parMulti'] = str(sub_rglob_list)
                continue
            # if passed:
            print(f'** and found the following date_paradigm: {date_}_{paradigm_}')
            list_df.at[index_list[i], 'parUnique'] = str(sub_rglob_list)
            list_df.at[index_list[i], 'uniqueExistence'] = True

        elif is_similar and not is_found:
            # print('is similar and is NOT found!!!')  # just a control check
            warnings.warn('the LATEST warning applies here, too!')

    list_df = list_df.reset_index(drop=True)  # getting rid of the stupid index; back to beautiful integers
    output_path = out_dir / f'scan_report_{now_}.csv'
    list_df.to_csv(output_path)  # saving the results of the disk scanning

    print(f'scanning of the drive completed... report log can be found here: \n'
          f'{output_path}')

    return list_df
