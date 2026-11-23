import os, pprint
from PIL import Image
E = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')) + '/episodes'; O = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'assets', 'videos')); os.makedirs(O, exist_ok=True)
# (date, titre, type, id TikTok, chemin Instagram, image de couverture)
V = [
 ('2026-11-23', 'Combien il faut gagner pour faire partie des 10 % les mieux payés ?', 'Vidéo', None, 'reel/DgE2MuVxFaM', '2026-11-24_top10_riches/couverture.png'),
 ('2026-11-21', "Buy, borrow, die : vivre comme un milliardaire sans presque payer d'impôt", 'Vidéo', None, 'reel/DgArlrFxBNN', '2026-11-21_buy_borrow_die/couverture.png'),
 ('2026-11-21', 'Fiche entreprise n°1 : que vaut Nvidia ?', 'Carrousel', '7710547145409056032', 'p/Df_2BH0Ef5Z', '2026-11-22_fiche_nvidia/out/tiktok_1.png'),
 ('2026-11-20', 'Les News : Nvidia, Anthropic, GTA 6, Walmart, Wall Street', 'Carrousel', '7710154619095092513', 'p/Df9GqsdEUOK', '2026-11-20_les_news/out/tiktok_1.png'),
 ('2026-11-19', "GTA 6 sort aujourd'hui : et si tu avais acheté des actions Take-Two plutôt que GTA 5 ?", 'Vidéo', '7709778351606484257', 'reel/Df6gLndxqzh', '2026-11-19_take_two/couverture.png'),
 ('2026-11-17', 'Le lexique de la bourse', 'Carrousel', '7709038655997873441', 'p/Df1YHfjEVxa', '2026-11-17_lexique/out/tiktok_1.png'),
 ('2026-11-16', 'Le Loto toute ta vie contre la même somme placée', 'Vidéo', '7708668836953820448', 'reel/Dfy0PE6RsEy', '2026-11-16_loto/couverture.png'),
 ('2026-11-14', 'Combien placer par mois pour devenir millionnaire ?', 'Vidéo', '7707944420561161504', 'reel/Dftylyxx0bh', '2026-11-14_millionnaire/couverture.png'),
 ('2026-11-13', 'Les News : le PDG de Nvidia démissionne', 'Carrousel', '7707556708968582422', 'p/DfrFH6NkXy9', '2026-11-13_les_news/out/tiktok_1.png'),
 ('2026-11-12', "L'or : valeur refuge ou placement qui dort ?", 'Vidéo', '7707186405159537952', 'reel/Dfohzs8xEvQ', '2026-11-12_or/couverture.png'),
 ('2026-11-11', 'Action ou obligation : propriétaire ou prêteur ?', 'Vidéo', '7706810365534817568', 'reel/Dfl62PjR3r3', '2026-11-11_actions_obligations/couverture.png'),
 ('2026-11-10', "Boeing : de la confiance absolue aux portes qui s'envolent", 'Vidéo', '7706457101366775072', 'reel/DfjYBFexB5y', '2026-11-10_boeing/couverture.png'),
 ('2026-11-09', "Comment commencer à t'enrichir ?", 'Vidéo', '7706145405276359969', 'reel/DfhTadiRB5m', '2026-11-09_senrichir/couverture.png'),
 ('2026-11-07', 'Pourquoi tu restes pauvre ?', 'Vidéo', '7705340095951392033', 'reel/DfbtR-HRa2c', '2026-11-07_pauvre/couverture.png'),
 ('2026-11-06', 'Combien il te faut pour vivre de tes dividendes ?', 'Vidéo', '7705042332793556257', 'reel/DfZpb5qRqjs', '2026-11-16_dividendes/couverture.png'),
 ('2026-11-05', 'Les News : résultats contre bourse (Apple, Palantir, AMD…)', 'Carrousel', '7704609363557633312', 'p/DfWkAaykZci', '2026-11-06_les_news/out/tiktok_1.png'),
 ('2026-11-04', 'Ubisoft : −95 % depuis son record', 'Vidéo', '7704369685340507425', 'reel/DfU_bdexzsx', '2026-11-05_ubisoft/couverture.png'),
 ('2026-11-03', 'Ton iPhone ou des actions Apple ?', 'Vidéo', '7703926277924801824', 'reel/DfR7mmcRW9P', '2026-11-04_iphone_actions/couverture.png'),
 ('2026-11-03', 'Palantir : génie ou bulle ?', 'Vidéo', '7703841962729770272', 'reel/DfRUyuTxGVL', '2026-11-03_palantir/couverture.png'),
 ('2026-11-02', "C'est quoi un ETF MSCI World ?", 'Vidéo', '7703529906122034464', 'reel/DfPKPUmxRgv', '2026-11-02_etf_msci_world/couverture.png'),
 ('2026-10-31', 'Les News : résultats contre bourse (Microsoft, Alphabet, Amazon, Intel)', 'Carrousel', '7702807478500724000', 'p/DfJt69_EfrP', '2026-10-31_gafam_carrousel/out/tiktok_1.png'),
 ('2026-10-30', 'Les intérêts composés', 'Vidéo', '7702421765330455840', 'reel/DfHd8MexK8w', '2026-10-30_interets_composes/couverture.png'),
 ('2026-10-29', 'Comprendre le prix du carburant en France', 'Vidéo', '7702046743424453920', 'reel/DfE3d3Lxo3M', '2026-10-29_carburant/couverture.png'),
 ('2026-10-28', 'Hermès : −57 % depuis le record', 'Vidéo', '7701678895824669984', 'reel/DfCUGHlRc5i', '2026-10-28_hermes/couverture.png'),
 ('2026-10-27', 'Kering (Gucci) : −78 % depuis le sommet', 'Vidéo', '7701312236496768289', 'reel/De_w9r_Rt0l', None),
 ('2026-10-26', 'AMD : la puce qui revient de très loin', 'Vidéo', '7700916898443119905', 'reel/De8_zUsxdae', '2026-10-26_amd/couverture.png'),
 ('2026-10-25', 'Novo Nordisk (Ozempic) : −74 %', 'Vidéo', '7700514706540236064', 'reel/De6P514o6_5', '2026-10-25_novo_nordisk/couverture.png'),
 ('2026-10-24', 'Série Krachs, ép. 2 : la bulle internet de 2000', 'Vidéo', '7700137755430505760', 'reel/De3nx4mxKIo', None),
 ('2026-10-23', 'Netflix, Tesla, Meta : les résultats', 'Vidéo', '7699804935331843361', 'reel/DezYSO8ug65', None),
 ('2026-10-22', 'PEA ou CTO ?', 'Vidéo', '7699583850996895009', 'reel/De1Uzlcx90b', None),
 ('2026-10-21', 'Coca-Cola : 848 millions de dollars par an pour Buffett', 'Vidéo', '7699060312200285473', 'reel/Dew2a7hRYUt', None),
 ('2026-10-20', "Intel : de 18 $ à plus de 140 $", 'Vidéo', '7698685768293731616', 'reel/DeyjbinRvN1', None),
 ('2026-10-19', 'Meta : 1 000 € le jour du changement de nom', 'Vidéo', '7698322188255956257', 'reel/DexX12JRYhh', None),
 ('2026-10-17', 'Série Krachs, ép. 1 : 2008', 'Vidéo', '7697557532348386592', None, None),
 ('2026-10-16', 'SpaceX : 1 000 € au sommet', 'Vidéo', '7697148430807780640', 'reel/DexD6ppxqUx', None),
 ('2026-10-15', 'Micron : 1 000 € il y a 5 ans', 'Vidéo', '7696932405025738017', None, None),
 ('2026-10-15', 'Bitcoin : 2 pizzas = 742 millions d\'euros', 'Vidéo', '7696850629188160801', 'reel/Dewu6C5oJXw', None),
]
out = []
for i, (d, t, ty, tk, ig, cv) in enumerate(V):
    vig = None
    if cv and os.path.exists(f'{E}/{cv}'):
        vig = f'{d}_{i:02d}.webp'
        Image.open(f'{E}/{cv}').convert('RGB').resize((720, 1280), Image.LANCZOS).save(f'{O}/{vig}', quality=84, method=6)
    elif cv: print('manque', cv)
    out.append((d, t, ty, tk, ig, vig))
print(sum(1 for x in out if x[5]), 'vignettes sur', len(out))
open('/tmp/videos.txt', 'w').write('VIDEOS = ' + pprint.pformat(out, width=200) + '\n')
