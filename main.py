import time

from funcs import *
from lib import *
from css import *

global updf, bef, comb, cb, sends, sent

def pmain():
    st.write(titlePMI, unsafe_allow_html=True)

    col0f, col3f = st.columns([7, 1])
    # col3 = st.empty()
    with col3f:
        with open('data/template.xlsx', 'rb') as f:
            st.download_button(label='Unduh template',
                               data=f, file_name='template.xlsx')
    st.header('')
    global df1, updf
    # upload file

    ufile = st.empty()
    ufile = st.file_uploader(
        label="Upload data history transaksi donor(Excel / CSV)", type=['xlsx', 'csv'])

    df1 = pd.read_csv('data/last.csv')
    jumpendonor = st.empty()
    jumpendonor.write('Jumlah pendonor: ' + str(df1.NomerDonor.nunique()))
    vdf = st.empty()
    vdf.write(df1.head(5))

    alg = ['Rule Based Classifier (RBC)', 'Artificial Neural Network (ANN)', 'Gabungan (ANN(+RBC))']
    global algo
    algo = st.radio(
        "Pilih Algoritma:",
        (alg))
    if ufile is not None:
        try:
            df1 = pd.read_excel(ufile)
        except Exception as e:
            df1 = pd.read_csv(ufile)
        vdf.write(df1.head(5))
        jumpendonor.write('Jumlah pendonor: ' + str(df1.NomerDonor.nunique()))
        df1.to_csv('data/last.csv', index=False)
        updf = 1

    df1 = changegol(df1)
    col3, col7, col0 = st.columns([1, 6, 1])
    lewat = col0.button('Lewati Prediksi')
    toclass = col3.button('Lihat Rekomendasi')
    if 'NoTlp' in df1:
        df1['NoTlp'] = '+62' + df1['NoTlp'].astype(str)
    else:
        df1['NoTlp'] = '+6281248897057'
    if 'Email' not in df1:
        df1['Email'] = 'skripsiwid@gmail.com'
    if toclass:
        vdf.write(df1.head(5))
        ufile = st.empty()
        st.session_state.runpage = ppleasewait
        st.experimental_rerun()
    if lewat:
        st.session_state.runpage = pimportrec
        st.experimental_rerun()


def ppleasewait():
    global comb, bef, updf, cb, wktu, imrec

    # st.write(str(updf))
    # st.write(bef)
    # st.write(algo)
    wktu1 = datetime.datetime.now()
    if updf == 1 or bef != algo:
        imrec = 0
        st.write(wbef+'Mencari rekomendasi ...'+waf, unsafe_allow_html=True)
        if algo == 'Rule Based Classifier (RBC)':
            # st.write('rbc')
            donor = rating(df1)
            rbc = RBCimplementation(df1)
            rbc.reset_index(drop = True, inplace = True)
            rated = ratenopred(donor, rbc)
            comb = alsranking(rated)
            dfu = df1.drop_duplicates(subset=['NomerDonor'], keep='last')
            combb = pd.merge(comb, dfu, on=['NomerDonor'], how='left')
            comb = pd.merge(combb, rbc, on=['NomerDonor'], how='left')
            # recc = recc.loc[(recc['BloodType'] == btb) & (recc['Recency'] > 60)]
            comb. rename(columns = {'TanggalDonor':'LastDonor'}, inplace = True)
            bef = 'Rule Based Classifier (RBC)'
            updf = 0
            cb = []

        # ann
        elif algo == 'Artificial Neural Network (ANN)':
            # st.write('ann')
            donor = rating(df1)
            kls = ANNclass(modelclass, df1)
            pred = ANNpred(modelpred, df1)
            pred.reset_index(drop = True, inplace = True)
            # kls.reset_index(drop = True, inplace = True)
            annpred = pd.merge(kls, pred, on=['NomerDonor'])
            rated = ratewpred(donor, annpred)
            comb = alsranking(rated)
            dfu = df1.drop_duplicates(subset=['NomerDonor'], keep='last')
            combb = pd.merge(comb, dfu, on=['NomerDonor'], how='left')
            comb = pd.merge(combb, kls, on=['NomerDonor'], how='left')
            # recc = recc.loc[(recc['BloodType'] == btb) & (recc['Recency'] > 60)]
            comb. rename(columns = {'TanggalDonor':'LastDonor'}, inplace = True)
            bef = 'Artificial Neural Network (ANN)'
            updf = 0
            cb = []

    # ann+rbc
        else:
            # st.write('Gabungan (ANN(+RBC))')
            donor = rating(df1)
            kls = ANNclass(modelannrbc, df1)
            pred = ANNpred(modelpred, df1)
            pred.reset_index(drop = True, inplace = True)
            # kls.reset_index(drop = True, inplace = True)
            annpred = pd.merge(kls, pred, on=['NomerDonor'])
            rated = ratewpred(donor, annpred)
            comb = alsranking(rated)
            dfu = df1.drop_duplicates(subset=['NomerDonor'], keep='last')
            combb = pd.merge(comb, dfu, on=['NomerDonor'], how='left')
            comb = pd.merge(combb, kls, on=['NomerDonor'], how='left')
            # recc = recc.loc[(recc['BloodType'] == btb) & (recc['Recency'] > 60)]
            comb. rename(columns = {'TanggalDonor':'LastDonor'}, inplace = True)
            bef = 'Gabungan (ANN(+RBC))'
            updf = 0
            cb = []


    # else:
    #     st.write('sblme')
    # time.sleep(10)
    wktu2 = datetime.datetime.now()
    wktu = wktu2 - wktu1
    wktu = wktu.total_seconds()
    st.session_state.runpage = pchoosedonor
    st.experimental_rerun()


def pchoosedonor():
    st.write(titlePMI, unsafe_allow_html=True)
    global comb, cb

    st.write('Waktu kalkulasi: ' + str(wktu) + ' detik')
    to = st.columns([1, 9, 1])
    backmain = to[0].button('Ke Main')
    toclass = to[2].button('Broadcast')

    sb = st.columns([2,1,2,1,2])
    jk = comb['JKel'].unique().tolist()
    bt = sorted(comb['GolDrh'].unique())
    jk.insert(0, 'Semua')
    l = ['Semua', '<= 25', '26 - 40', '41 - 50', '51 - 64', '>= 65']
    gjk = sb[0].selectbox('Jenis Kelamin:', jk)
    gbt = sb[2].selectbox('Golongan Darah:', bt)
    gage = sb[4].selectbox('Umur:', l)

    if gjk == 'Semua':
        if gage == 'Semua':
            show = comb.loc[(comb['GolDrhRec'] == gbt) & (comb['GolDrh'] == gbt)]
        elif gage == '<= 25':
            show = comb.loc[(comb['GolDrhRec'] == gbt) & (comb['GolDrh'] == gbt) & (comb['Umur'] <= 25)]
        elif gage == '26 - 40':
            show = comb.loc[(comb['GolDrhRec'] == gbt) & (comb['GolDrh'] == gbt) & (comb['Umur'] >= 26) & (comb['Umur'] <= 40)]
        elif gage == '41 - 50':
            show = comb.loc[(comb['GolDrhRec'] == gbt) & (comb['GolDrh'] == gbt) & (comb['Umur'] >= 41) & (comb['Umur'] <= 50)]
        elif gage == '51 - 64':
            show = comb.loc[(comb['GolDrhRec'] == gbt) & (comb['GolDrh'] == gbt) & (comb['Umur'] >= 51) & (comb['Umur'] <= 64)]
        else:
            show = comb.loc[(comb['GolDrhRec'] == gbt) & (comb['GolDrh'] == gbt) & (comb['Umur'] >= 65)]
    else:
        if gage == 'Semua':
            show = comb.loc[(comb['GolDrhRec'] == gbt) & (comb['GolDrh'] == gbt) & (comb['JKel'] == gjk)]
        elif gage == '<= 25':
            show = comb.loc[(comb['GolDrhRec'] == gbt) & (comb['GolDrh'] == gbt) & (comb['Umur'] <= 25) & (comb['JKel'] == gjk)]
        elif gage == '26 - 40':
            show = comb.loc[(comb['GolDrhRec'] == gbt) & (comb['GolDrh'] == gbt) & (comb['Umur'] >= 26) & (comb['Umur'] <= 40) & (comb['JKel'] == gjk)]
        elif gage == '41 - 50':
            show = comb.loc[(comb['GolDrhRec'] == gbt) & (comb['GolDrh'] == gbt) & (comb['Umur'] >= 41) & (comb['Umur'] <= 50) & (comb['JKel'] == gjk)]
        elif gage == '51 - 64':
            show = comb.loc[(comb['GolDrhRec'] == gbt) & (comb['GolDrh'] == gbt) & (comb['Umur'] >= 51) & (comb['Umur'] <= 64) & (comb['JKel'] == gjk)]
        else:
            show = comb.loc[(comb['GolDrhRec'] == gbt) & (comb['GolDrh'] == gbt) & (comb['Umur'] >= 65) & (comb['JKel'] == gjk)]

    st.write('Pilih pendonor:')

    # st.write(show)
    # recs = comb[['NomerDonor', 'NamaDonor', 'JKel', 'Umur', 'GolDrh', 'LastDonor']]

    headercol = st.columns([1, 1, 2, 3, 2, 2, 2, 2, 1, 1])
    headercol[0].write('')
    headercol[1].write('Ranking')
    headercol[2].write('Nomer Donor')
    headercol[3].write('Nama Donor')
    headercol[4].write('JKel')
    headercol[5].write('Umur')
    headercol[6].write('Gol Darah')
    headercol[7].write('Donor Terakhir')
    headercol[8].write('Kategori')
    headercol[9].write('Rating')

    count = 1
    tenddate = pd.to_datetime(date.today())
    for i, r in show.iterrows():
        tbl = st.columns([1, 1, 2, 3, 2, 2, 2, 2, 1, 1])
        if [r.NomerDonor, True] in cb:
            cbs = tbl[0].checkbox('', key=r.NomerDonor, value=True)
            # st.warning(cbs)
            if cbs == False:
                cb.remove([r.NomerDonor, True])
                cb.append([r.NomerDonor, cbs])
        else:
            cbs = tbl[0].checkbox('', key=r.NomerDonor)
            cb.append([r.NomerDonor, cbs])
        tbl[1].write(str(count))
        tbl[2].write(str(r.NomerDonor))
        tbl[3].write(r.NamaDonor)
        tbl[4].write(r.JKel)
        tbl[5].write(str(r.Umur))
        tbl[6].write(r.GolDrh)
        tbl[7].write(str((tenddate - r.LastDonor).days) + ' hari')
        tbl[8].write(str(math.floor(r.Category)))
        tbl[9].write(str(round(r.Rating,2)))
        count+=1

    hrini = pd.to_datetime(date.today())
    with st.sidebar:
        st.write("**Simpan Hasil Rekomendasi**")
    db = st.sidebar.columns([1,3,1])
    exprt = show[['NomerDonor', 'NamaDonor', 'JKel', 'Umur', 'GolDrh', 'LastDonor', 'Category', 'Rating']]
    db[1].download_button(label='Unduh Rekomendasi',
                               data=to_excel(exprt), file_name='Rekomendasi '+str(hrini)+'.xlsx')

    if backmain:
        st.session_state.runpage = pmain
        st.experimental_rerun()

    if toclass:
        global dtf
        dtf = pd.DataFrame(cb, columns=['NomerDonor', 'TF'])
        dtf = dtf.loc[(dtf['TF'] == True)]
        st.session_state.runpage = pbroadcast
        st.experimental_rerun()


def pbroadcast():
    st.write(titlePMI, unsafe_allow_html=True)
    global comb, sends, cb, sent

    final = st.columns([3, 9, 1])
    tobc = final[0].button('Pilih Pendonor')
    tomain = final[2].button('Ke Main')
    if tobc:
        st.session_state.runpage = pchoosedonor
        st.experimental_rerun()
    if tomain:
        st.session_state.runpage = pmain
        st.experimental_rerun()

    st.write('Jumlah pendonor yang dipilih: ' + str(dtf['NomerDonor'].count()))

    st.write('Pilih media:')

    cb1, cb2, cb3 = st.columns([1, 1, 1])
    cb11 = cb1.checkbox('Email')
    cb22 = cb2.checkbox('SMS')
    cb33 = cb3.checkbox('WhatsApp')

    dfu = df1.drop_duplicates(subset=['NomerDonor'], keep='last')
    sends = pd.merge(dtf, dfu, on=['NomerDonor'], how='left')

    tampil = sends[['NomerDonor', 'NamaDonor', 'Umur', 'JKel', 'GolDrh']]
    colpenerima = st.columns([1,2,1])
    colpenerima[1].write(tampil.head(5))

    txt = st.text_area('Message:', '''
Yth.
Sdr. / Sdri.
[NamaDonor], 

Kami dari UTD PMI Surabaya ingin mengundang anda untuk mendonorkan darah dalam waktu dekat, karena ketersediaan darah semakin menipis. Terima kasih.
    
Best regards,
UTD PMI Surabaya 
Jl. Embong Ploso nomor 7 - 15, Surabaya
(031) 5313289''', height=300)

    atas = st.columns([11, 1])
    next = atas[1].button('Broadcast')

    if next:
        comb = pd.concat([comb, sends]).drop_duplicates(subset=['NomerDonor', 'NamaDonor'], keep=False)
        sent = sends
        cb = []
        dft = ''
        st.write(bukadiv, unsafe_allow_html=True)
        placeholder = st.empty()

        if cb11 == True:
            # st.write('Mengirim Email ..')
            dari = 'skripsiwid@gmail.com'
            passdari = 'excqgspweodbblyr'

            msg = EmailMessage()
            msg['Subject'] = 'Ayo Donor'
            msg['From'] = dari

            for i, r in sends.iterrows():
                c = txt
                c = c.replace('[NomerDonor]', str(r.NomerDonor))
                c = c.replace('[NamaDonor]', str(r.NamaDonor))
                c = c.replace('[Umur]', str(r.Umur))
                c = c.replace('[JKel]', str(r.JKel))
                c = c.replace('[GolDrh]', str(r.GolDrh))
                msg.set_content(c)
                msg['To'] = r.Email
                s = smtplib.SMTP('smtp.gmail.com', 587)
                s.starttls()
                s.login(dari, passdari)
                s.send_message(msg)
                s.quit()
                del msg['To']
            # server.quit()
            # st.write('Email terkirim.')
        with placeholder:
            kot = st.columns([10,1,1,1,10])
            kot[1].write(iya, unsafe_allow_html=True)
            kot[2].write(ngga, unsafe_allow_html=True)
            kot[3].write(ngga, unsafe_allow_html=True)

        if cb22 == True:
            # st.write('Mengirim SMS ..')
            account = "AC92680aef5ea0651548b2e06fa724d95e"
            token = "2effe469208dd50d156325d8290e854b"
            client = Client(account, token)

            dari = '+18125058774'
            for i, r in sends.iterrows():
                c = txt
                c = c.replace('[NomerDonor]', str(r.NomerDonor))
                c = c.replace('[NamaDonor]', str(r.NamaDonor))
                c = c.replace('[Umur]', str(r.Umur))
                c = c.replace('[JKel]', str(r.JKel))
                c = c.replace('[GolDrh]', str(r.GolDrh))
                # to = r.NoTlp
                to = '+6281358584635'
                client.messages.create(body=c, from_=dari, to=to)
                # st.write(r.NoTlp)
            # st.write('SMS terkirim.')
        with placeholder:
            kot = st.columns([10,1,1,1,10])
            kot[1].write(iya, unsafe_allow_html=True)
            kot[2].write(iya, unsafe_allow_html=True)
            kot[3].write(ngga, unsafe_allow_html=True)

        if cb33 == True:
            # st.write('WhatsApp')
            # st.write('Mengirim WhatsApp ..')

            BASE_URL = 'https://api.nusasms.com/nusasms_api/1.0'
            HEADERS = {
                "Accept": "application/json",
                "APIKey": "472A3011788B158CA57618F2ABC7C1DF "
            }

            for i, r in sends.iterrows():
                c = txt
                c = c.replace('[NomerDonor]', str(r.NomerDonor))
                c = c.replace('[NamaDonor]', str(r.NamaDonor))
                c = c.replace('[Umur]', str(r.Umur))
                c = c.replace('[JKel]', str(r.JKel))
                c = c.replace('[GolDrh]', str(r.GolDrh))
                PAYLOADS = {
                    'destination': r.NoTlp,
                    'sender': None,
                    'message': c
                }
                r = requests.post(
                    f'{BASE_URL}/whatsapp/message',
                    headers=HEADERS,
                    json=PAYLOADS,
                    verify=False
                )

            # st.write('WhatsApp terkirim.')
        with placeholder:
            kot = st.columns([10,1,1,1,10])
            kot[1].write(iya, unsafe_allow_html=True)
            kot[2].write(iya, unsafe_allow_html=True)
            kot[3].write(iya, unsafe_allow_html=True)
        st.write(tutupdiv, unsafe_allow_html=True)
        st.write(slesaii, unsafe_allow_html=True)

        downloadtampil = st.columns([5,5,5])
        hrini = pd.to_datetime(date.today())
        st.write(bukadiv, unsafe_allow_html=True)
        downloadtampil[1].download_button(label='Unduh History Broadcast',
                                          data=to_excel(tampil), file_name='Broadcast '+str(hrini)+'.xlsx')
        st.write(tutupdiv, unsafe_allow_html=True)


def pimportrec():
    st.write(titlePMI, unsafe_allow_html=True)
    global comb, cb, bef, imrec

    to = st.columns([1, 9, 1])
    backmain = to[0].button('Ke Main')

    fp = st.file_uploader(label="Import Hasil Rekomendasi", type=['xlsx', 'csv'])
    if fp is not None:
        try:
            comb = pd.read_excel(fp)
        except Exception as e:
            comb = pd.read_csv(fp)
    st.write('')

    if fp is not None or imrec == 1:
        cb = []
        bef = ''
        imrec = 1
        toclass = to[2].button('Broadcast')
        sb = st.columns([2,1,2,1,2])
        jk = comb['JKel'].unique().tolist()
        bt = sorted(comb['GolDrh'].unique())
        jk.insert(0, 'Semua')
        l = ['Semua', '<= 25', '26 - 40', '41 - 50', '51 - 64', '>= 65']
        gjk = sb[0].selectbox('Jenis Kelamin:', jk)
        gbt = sb[2].selectbox('Golongan Darah:', bt)
        gage = sb[4].selectbox('Umur:', l)

        if gjk == 'Semua':
            if gage == 'Semua':
                show = comb.loc[(comb['GolDrh'] == gbt)]
            elif gage == '<= 25':
                show = comb.loc[(comb['GolDrh'] == gbt) & (comb['Umur'] <= 25)]
            elif gage == '26 - 40':
                show = comb.loc[(comb['GolDrh'] == gbt) & (comb['Umur'] >= 26) & (comb['Umur'] <= 40)]
            elif gage == '41 - 50':
                show = comb.loc[(comb['GolDrh'] == gbt) & (comb['Umur'] >= 41) & (comb['Umur'] <= 50)]
            elif gage == '51 - 64':
                show = comb.loc[(comb['GolDrh'] == gbt) & (comb['Umur'] >= 51) & (comb['Umur'] <= 64)]
            else:
                show = comb.loc[(comb['GolDrh'] == gbt) & (comb['Umur'] >= 65)]
        else:
            if gage == 'Semua':
                show = comb.loc[(comb['GolDrh'] == gbt) & (comb['JKel'] == gjk)]
            elif gage == '<= 25':
                show = comb.loc[(comb['GolDrh'] == gbt) & (comb['Umur'] <= 25) & (comb['JKel'] == gjk)]
            elif gage == '26 - 40':
                show = comb.loc[(comb['GolDrh'] == gbt) & (comb['Umur'] >= 26) & (comb['Umur'] <= 40) & (comb['JKel'] == gjk)]
            elif gage == '41 - 50':
                show = comb.loc[(comb['GolDrh'] == gbt) & (comb['Umur'] >= 41) & (comb['Umur'] <= 50) & (comb['JKel'] == gjk)]
            elif gage == '51 - 64':
                show = comb.loc[(comb['GolDrh'] == gbt) & (comb['Umur'] >= 51) & (comb['Umur'] <= 64) & (comb['JKel'] == gjk)]
            else:
                show = comb.loc[(comb['GolDrh'] == gbt) & (comb['Umur'] >= 65) & (comb['JKel'] == gjk)]

        st.write('Pilih pendonor:')

        # st.write(show)
        # recs = comb[['NomerDonor', 'NamaDonor', 'JKel', 'Umur', 'GolDrh', 'LastDonor']]

        headercol = st.columns([1, 1, 2, 3, 2, 2, 2, 2, 1, 1])
        headercol[0].write('')
        headercol[1].write('Ranking')
        headercol[2].write('Nomer Donor')
        headercol[3].write('Nama Donor')
        headercol[4].write('JKel')
        headercol[5].write('Umur')
        headercol[6].write('Gol Darah')
        headercol[7].write('Donor Terakhir')
        headercol[8].write('Kategori')
        headercol[9].write('Rating')

        count = 1
        tenddate = pd.to_datetime(date.today())
        for i, r in show.iterrows():
            tbl = st.columns([1, 1, 2, 3, 2, 2, 2, 2, 1, 1])
            if [r.NomerDonor, True] in cb:
                cbs = tbl[0].checkbox('', key=r.NomerDonor, value=True)
                # st.warning(cbs)
                if cbs == False:
                    cb.remove([r.NomerDonor, True])
                    cb.append([r.NomerDonor, cbs])
            else:
                cbs = tbl[0].checkbox('', key=r.NomerDonor)
                cb.append([r.NomerDonor, cbs])
            tbl[1].write(str(count))
            tbl[2].write(str(r.NomerDonor))
            tbl[3].write(r.NamaDonor)
            tbl[4].write(r.JKel)
            tbl[5].write(str(r.Umur))
            tbl[6].write(r.GolDrh)
            tbl[7].write(str((tenddate - r.LastDonor).days) + ' hari')
            tbl[8].write(str(math.floor(r.Category)))
            tbl[9].write(str(round(r.Rating,2)))
            count+=1

        if toclass:
            global dtf
            dtf = pd.DataFrame(cb, columns=['NomerDonor', 'TF'])
            dtf = dtf.loc[(dtf['TF'] == True)]
            st.session_state.runpage = pbroadcast2
            st.experimental_rerun()

    if backmain:
        st.session_state.runpage = pmain
        st.experimental_rerun()



def pbroadcast2():
    st.write(titlePMI, unsafe_allow_html=True)
    global comb, sends, cb, sent

    final = st.columns([3, 9, 1])
    tobc = final[0].button('Pilih Pendonor')
    tomain = final[2].button('Ke Main')
    if tobc:
        st.session_state.runpage = pimportrec
        st.experimental_rerun()
    if tomain:
        st.session_state.runpage = pmain
        st.experimental_rerun()

    st.write('Jumlah pendonor yang dipilih: ' + str(dtf['NomerDonor'].count()))

    st.write('Pilih media:')

    cb1, cb2, cb3 = st.columns([1, 1, 1])
    cb11 = cb1.checkbox('Email')
    cb22 = cb2.checkbox('SMS')
    cb33 = cb3.checkbox('WhatsApp')

    dfu = df1.drop_duplicates(subset=['NomerDonor'], keep='last')
    sends = pd.merge(dtf, dfu, on=['NomerDonor'], how='left')

    tampil = sends[['NomerDonor', 'NamaDonor', 'Umur', 'JKel', 'GolDrh']]
    colpenerima = st.columns([1,2,1])
    colpenerima[1].write(tampil.head(5))

    txt = st.text_area('Message:', '''
Yth.
Sdr. / Sdri.
[NamaDonor], 

Kami dari UTD PMI Surabaya ingin mengundang anda untuk mendonorkan darah dalam waktu dekat, karena ketersediaan darah semakin menipis. Terima kasih.
    
Best regards,
UTD PMI Surabaya 
Jl. Embong Ploso nomor 7 - 15, Surabaya
(031) 5313289''', height=300)

    atas = st.columns([11, 1])
    next = atas[1].button('Broadcast')

    if next:
        comb = pd.concat([comb, sends]).drop_duplicates(subset=['NomerDonor', 'NamaDonor'], keep=False)
        sent = sends
        cb = []
        dft = ''
        st.write(bukadiv, unsafe_allow_html=True)
        placeholder = st.empty()

        if cb11 == True:
            # st.write('Mengirim Email ..')
            dari = 'skripsiwid@gmail.com'
            passdari = 'excqgspweodbblyr'

            msg = EmailMessage()
            msg['Subject'] = 'Ayo Donor'
            msg['From'] = dari

            for i, r in sends.iterrows():
                c = txt
                c = c.replace('[NomerDonor]', str(r.NomerDonor))
                c = c.replace('[NamaDonor]', str(r.NamaDonor))
                c = c.replace('[Umur]', str(r.Umur))
                c = c.replace('[JKel]', str(r.JKel))
                c = c.replace('[GolDrh]', str(r.GolDrh))
                msg.set_content(c)
                msg['To'] = r.Email
                s = smtplib.SMTP('smtp.gmail.com', 587)
                s.starttls()
                s.login(dari, passdari)
                s.send_message(msg)
                s.quit()
                del msg['To']
            # server.quit()
            # st.write('Email terkirim.')
        with placeholder:
            kot = st.columns([10,1,1,1,10])
            kot[1].write(iya, unsafe_allow_html=True)
            kot[2].write(ngga, unsafe_allow_html=True)
            kot[3].write(ngga, unsafe_allow_html=True)

        if cb22 == True:
            # st.write('Mengirim SMS ..')
            account = "AC92680aef5ea0651548b2e06fa724d95e"
            token = "2effe469208dd50d156325d8290e854b"
            client = Client(account, token)

            dari = '+18125058774'
            for i, r in sends.iterrows():
                c = txt
                c = c.replace('[NomerDonor]', str(r.NomerDonor))
                c = c.replace('[NamaDonor]', str(r.NamaDonor))
                c = c.replace('[Umur]', str(r.Umur))
                c = c.replace('[JKel]', str(r.JKel))
                c = c.replace('[GolDrh]', str(r.GolDrh))
                # to = r.NoTlp
                to = '+6281358584635'
            client.messages.create(body=c, from_=dari, to=to)
                # st.write(r.NoTlp)
            # st.write('SMS terkirim.')
        with placeholder:
            kot = st.columns([10,1,1,1,10])
            kot[1].write(iya, unsafe_allow_html=True)
            kot[2].write(iya, unsafe_allow_html=True)
            kot[3].write(ngga, unsafe_allow_html=True)

        if cb33 == True:
            # st.write('WhatsApp')
            # st.write('Mengirim WhatsApp ..')

            BASE_URL = 'https://api.nusasms.com/nusasms_api/1.0'
            HEADERS = {
                "Accept": "application/json",
                "APIKey": "472A3011788B158CA57618F2ABC7C1DF "
            }

            for i, r in sends.iterrows():
                c = txt
                c = c.replace('[NomerDonor]', str(r.NomerDonor))
                c = c.replace('[NamaDonor]', str(r.NamaDonor))
                c = c.replace('[Umur]', str(r.Umur))
                c = c.replace('[JKel]', str(r.JKel))
                c = c.replace('[GolDrh]', str(r.GolDrh))
                PAYLOADS = {
                    'destination': r.NoTlp,
                    'sender': None,
                    'message': c
                }
                r = requests.post(
                    f'{BASE_URL}/whatsapp/message',
                    headers=HEADERS,
                    json=PAYLOADS,
                    verify=False
                )

            # st.write('WhatsApp terkirim.')
        with placeholder:
            kot = st.columns([10,1,1,1,10])
            kot[1].write(iya, unsafe_allow_html=True)
            kot[2].write(iya, unsafe_allow_html=True)
            kot[3].write(iya, unsafe_allow_html=True)
        st.write(tutupdiv, unsafe_allow_html=True)
        st.write(slesaii, unsafe_allow_html=True)

        downloadtampil = st.columns([5,5,5])
        hrini = pd.to_datetime(date.today())
        st.write(bukadiv, unsafe_allow_html=True)
        downloadtampil[1].download_button(label='Unduh History Broadcast',
                                          data=to_excel(tampil), file_name='Broadcast '+str(hrini)+'.xlsx')
        st.write(tutupdiv, unsafe_allow_html=True)


if __name__ == '__main__':
    comb = ''
    sends = ''
    sent = ''
    updf = 0
    bef = ''
    imrec = 0
    bc = []
    cb = []
    st.set_page_config(layout="wide")
    if 'runpage' not in st.session_state:
        st.session_state.runpage = pmain
    st.session_state.runpage()


# recovery twilio: eCNsnRuit1LRSh3a41-Wh8IXpb8sRYN-MlSbqkrm
# sid = ACa96063702a909e7c420c5b951c08ff82
# auth token = b6b00d5972f3bab98d763bdc78032d01


# 2015 = 44647
# 2016 = 50026
# 2017 = 54968
# 2018 = 62105
# 2019 = 78653
# 2020 = 67536
# 2021 = 63614
# 2022 = 9810


# pimportrec - pbroadcast2
# pchoosedonor - pbroadcast