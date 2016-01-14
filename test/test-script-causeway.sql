PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE owner (
    address varchar(64) primary key,
    nonce varchar(32),
    balance integer,
    bad_attempts integer
, delegate varchar(64));
INSERT INTO "owner" VALUES('1HZwkjkeaoZfTSaJxDw6aKkxp45agDiEzN','',0,0,'1CptxARjqcfkVwGFSjR82zmPT8YtRMubub');
INSERT INTO "owner" VALUES('1Djp4Siv5iLJUgXq5peWCDcHVWV1Mv3opc','',0,0,'19skaV7ZDvSe2zKXB32fcay2NzajJcRG8B');
INSERT INTO "owner" VALUES('1M6DBU6LoaskwWxfpqaaZ1Z85nsixM97Tc','',0,0,'18UZN58o4fnJpfC7nMBQ5iapoLmqfPf3m5');
CREATE TABLE kv (
    key varchar(64) primary key,
    value blob,
    owner varchar(64),
    sale integer,    /* which sale/bucket is this stored under */
    foreign key(owner) references owner(address)
);
INSERT INTO "kv" VALUES('IEU36G2PGDCHT1X1BEDWYWZI0HBX7VY2','-----BEGIN BITCOIN SIGNED MESSAGE-----
Rein User Enrollment
User: Bob
Contact: bob@example.com
Master signing address: 1HZwkjkeaoZfTSaJxDw6aKkxp45agDiEzN
Delegate signing address: 1CptxARjqcfkVwGFSjR82zmPT8YtRMubub
Willing to mediate: False
-----BEGIN SIGNATURE-----
1HZwkjkeaoZfTSaJxDw6aKkxp45agDiEzN
G+I+yr15oWQJUlxC+FO5Bw8Oc1ExfGNPH0Bn0zBOSmjpZ+c/a8gvdabEaPLEdOI101lHLDmM42s94GUuUAUTFD0=
-----END BITCOIN SIGNED MESSAGE-----
','1HZwkjkeaoZfTSaJxDw6aKkxp45agDiEzN',1);
INSERT INTO "kv" VALUES('WC9L4DBYGBWNSKBY1WKSZIR3AIQP3ABG','-----BEGIN BITCOIN SIGNED MESSAGE-----
Rein User Enrollment
User: Alice
Contact: alice@example.com
Master signing address: 1Djp4Siv5iLJUgXq5peWCDcHVWV1Mv3opc
Delegate signing address: 19skaV7ZDvSe2zKXB32fcay2NzajJcRG8B
Willing to mediate: True
Mediator pubkey: 029fcafbe2dced6fe79865b265ea90387c5411658ca11449999d5020a9f67bb005
Mediation fee: 1.0%
-----BEGIN SIGNATURE-----
1Djp4Siv5iLJUgXq5peWCDcHVWV1Mv3opc
H2ynZXU3ZBfeJQsRasA8/RRLjdpRYnMVtz5YBU0Ztos8+eOyWZ1DuW8J8ydVen+Pp8bbk0K/kxK0NOy55veKDJw=
-----END BITCOIN SIGNED MESSAGE-----
','1Djp4Siv5iLJUgXq5peWCDcHVWV1Mv3opc',1);
INSERT INTO "kv" VALUES('BQXDTTFMMVBH4AHCV1KUPEQM7S4QM2PE','-----BEGIN BITCOIN SIGNED MESSAGE-----
Rein User Enrollment
User: Charlie
Contact: charlie@example.com
Master signing address: 1M6DBU6LoaskwWxfpqaaZ1Z85nsixM97Tc
Delegate signing address: 18UZN58o4fnJpfC7nMBQ5iapoLmqfPf3m5
Willing to mediate: False
-----BEGIN SIGNATURE-----
1M6DBU6LoaskwWxfpqaaZ1Z85nsixM97Tc
H2RKR84OHoAJcg0MogALwXR8MLo9zRvMNmRQr0t7MPhrg5Gx2pUYpGUx1hC4W60ljn40ghhEzQ/kDHH+z/lZPrM=
-----END BITCOIN SIGNED MESSAGE-----
','1M6DBU6LoaskwWxfpqaaZ1Z85nsixM97Tc',1);
INSERT INTO "kv" VALUES('0AMBJAFQY4I6BBVPJ72S7BR2ZBU2WZLS','-----BEGIN BITCOIN SIGNED MESSAGE-----
Rein Job
Job creator''s name: Bob
Job creator''s public key: 026bc363139ebc1cad8e6eee402507d2b4874f5450585f1e6a1cd30a63ecdfc9dc
Mediator''s name: Alice
Mediator''s public key: 029fcafbe2dced6fe79865b265ea90387c5411658ca11449999d5020a9f67bb005
Job name: A Software Widget
Category: Software
Description: I need a widget for my website. It needs to be done in Javascript and must show a message to each visitor, basically "Hello World!" is the message. In any case, the site is http://example.com so please check it out before bidding. Thanks!
Job ID: fyzfrxtrttcv8o04oj53
-----BEGIN SIGNATURE-----
1CptxARjqcfkVwGFSjR82zmPT8YtRMubub
H3qtO/IOayLkuRdUX/ElBXQVh/yIddcWq6XmfwpHvwajPhTmsHmJTgqRczMNGNRyU5UsM5N5qJB5rI8wK4aD+/0=
-----END BITCOIN SIGNED MESSAGE-----','1HZwkjkeaoZfTSaJxDw6aKkxp45agDiEzN',1);
INSERT INTO "kv" VALUES('LVE66MN83IKATVC61SAG0IARNZGSOIGQ','-----BEGIN BITCOIN SIGNED MESSAGE-----
Rein Job
Job creator''s name: Bob
Job creator''s public key: 026bc363139ebc1cad8e6eee402507d2b4874f5450585f1e6a1cd30a63ecdfc9dc
Mediator''s name: Alice
Mediator''s public key: 029fcafbe2dced6fe79865b265ea90387c5411658ca11449999d5020a9f67bb005
Job name: Winter Picnic Flyer
Category: Graphics
Description: My neighborhood is having its yearly Winter picnic. We live in a very mild climate. I need a flyer as a PDF that says in no uncertain terms that  there will be a picnic, it will happen at <date> at <time> and that <entertaining emotion> will be had! Thanks!
Job ID: 6g0j1m22lec5btt8b9t7
-----BEGIN SIGNATURE-----
1CptxARjqcfkVwGFSjR82zmPT8YtRMubub
IGWk0/xKwB6+TKGOOx0DATxJm/9PdlQN4H4Z2gfAbrbVMGnhnSwRY4J0hoZCsnmh6WM6mkbhU3fnGP3YuZEBCEs=
-----END BITCOIN SIGNED MESSAGE-----','1HZwkjkeaoZfTSaJxDw6aKkxp45agDiEzN',1);
INSERT INTO "kv" VALUES('5VIEIBKLVC69XD6JTY9PSMKX49Q95FWV','-----BEGIN BITCOIN SIGNED MESSAGE-----
Rein Bid
Worker''s name: Charlie
Worker''s public key: 02f719f009fb8eb20ccdbfda7d38f378ed2f103ac0a6768df830740c6835c46519
Job ID: fyzfrxtrttcv8o04oj53
Job creator''s name: Bob
Job creator''s public key: 026bc363139ebc1cad8e6eee402507d2b4874f5450585f1e6a1cd30a63ecdfc9dc
Description: Hi Bob, I can get this done for you no problem. I am a Javascript whiz and have done "Hello World!"-type jobs many times. I can have this done for you within 3 days of your offer. Thank you, sir.
Bid amount (BTC): 0.05
-----BEGIN SIGNATURE-----
18UZN58o4fnJpfC7nMBQ5iapoLmqfPf3m5
H1+txkpc6vXvncLrELwVVowfr64cwoOsV/pTQ+mNTiMuCYBFdCr1pAIyv/L5rFbpNDRC019aVxS6UVl6kRF4umE=
-----END BITCOIN SIGNED MESSAGE-----','1M6DBU6LoaskwWxfpqaaZ1Z85nsixM97Tc',1);
INSERT INTO "kv" VALUES('MZTNIL22VFZV07HH7K717GJ7R69VPK6S','-----BEGIN BITCOIN SIGNED MESSAGE-----
Rein Bid
Worker''s name: Charlie
Worker''s public key: 02f719f009fb8eb20ccdbfda7d38f378ed2f103ac0a6768df830740c6835c46519
Job ID: 6g0j1m22lec5btt8b9t7
Job creator''s name: Bob
Job creator''s public key: 026bc363139ebc1cad8e6eee402507d2b4874f5450585f1e6a1cd30a63ecdfc9dc
Description: In addition to my Javascript creds, I''m quite handy with Acme Photojobber and can create a few designs for you to choose from. TI will also include two rounds of revisions on your selected design for the bid amount. I can get this entire job done for you within 7 days. Thank you, sire.
Bid amount (BTC): 0.1
-----BEGIN SIGNATURE-----
18UZN58o4fnJpfC7nMBQ5iapoLmqfPf3m5
H34HeYI+xo+mQR5n97ZAtHWoDZkfSNMuRp3144SBF0ZYRN3TyJrrdHief4/3vXY1nxrsmS7GVKQyTLI3uBveC7c=
-----END BITCOIN SIGNED MESSAGE-----','1M6DBU6LoaskwWxfpqaaZ1Z85nsixM97Tc',1);
INSERT INTO "kv" VALUES('WFH5RH2L6CFAQQMHHTEFJ0WAQOZWOXWJ','-----BEGIN BITCOIN SIGNED MESSAGE-----
Rein Offer
Job creator''s name: Bob
Job creator''s public key: 026bc363139ebc1cad8e6eee402507d2b4874f5450585f1e6a1cd30a63ecdfc9dc
Worker''s name: Charlie
Worker''s public key: 02f719f009fb8eb20ccdbfda7d38f378ed2f103ac0a6768df830740c6835c46519
Mediator''s name: Bob
Mediator''s public key: 026bc363139ebc1cad8e6eee402507d2b4874f5450585f1e6a1cd30a63ecdfc9dc
Mediator escrow address: 3R1Pzho6Yca27AceUHBYnmg6S2NbT1LtLs
Mediator escrow redeem script: 21029fcafbe2dced6fe79865b265ea90387c5411658ca11449999d5020a9f67bb005ad5221026bc363139ebc1cad8e6eee402507d2b4874f5450585f1e6a1cd30a63ecdfc9dc2102f719f009fb8eb20ccdbfda7d38f378ed2f103ac0a6768df830740c6835c4651952ae
Primary escrow address: 3GJrubCa1wCFMUqnwPhuyeQXdWTD8hecdG
Primary escrow redeem script: 522102f719f009fb8eb20ccdbfda7d38f378ed2f103ac0a6768df830740c6835c4651921026bc363139ebc1cad8e6eee402507d2b4874f5450585f1e6a1cd30a63ecdfc9dc21029fcafbe2dced6fe79865b265ea90387c5411658ca11449999d5020a9f67bb00553ae
Description: I''m not sure what to write here but getting it done in a few days sounds good. Let us begin!
Bid amount (BTC): 0.05
Job ID: fyzfrxtrttcv8o04oj53
-----BEGIN SIGNATURE-----
1CptxARjqcfkVwGFSjR82zmPT8YtRMubub
IHBppS2AkGAnXYbjOx+Y5m9IFrdohq7NizcOzqVkapnvaY7nmuO3lFwbnV9AFWwTj5/QFTge3Jww8sT3f/kl3+o=
-----END BITCOIN SIGNED MESSAGE-----','1HZwkjkeaoZfTSaJxDw6aKkxp45agDiEzN',1);
INSERT INTO "kv" VALUES('FX8L8XTR1VZKIGRXHHR1L5T3R60WF8O5','-----BEGIN BITCOIN SIGNED MESSAGE-----
Rein Offer
Job creator''s name: Bob
Job creator''s public key: 026bc363139ebc1cad8e6eee402507d2b4874f5450585f1e6a1cd30a63ecdfc9dc
Worker''s name: Charlie
Worker''s public key: 02f719f009fb8eb20ccdbfda7d38f378ed2f103ac0a6768df830740c6835c46519
Mediator''s name: Bob
Mediator''s public key: 026bc363139ebc1cad8e6eee402507d2b4874f5450585f1e6a1cd30a63ecdfc9dc
Mediator escrow address: 3Di3fKuqVLoVirvxJ7gRHvbE5hxEFWViUU
Mediator escrow redeem script: 21029fcafbe2dced6fe79865b265ea90387c5411658ca11449999d5020a9f67bb005ad522102f719f009fb8eb20ccdbfda7d38f378ed2f103ac0a6768df830740c6835c4651921026bc363139ebc1cad8e6eee402507d2b4874f5450585f1e6a1cd30a63ecdfc9dc52ae
Primary escrow address: 3A3ghdXaaKCcMUTfL2XXMLJhnUZUimYF2n
Primary escrow redeem script: 5221029fcafbe2dced6fe79865b265ea90387c5411658ca11449999d5020a9f67bb0052102f719f009fb8eb20ccdbfda7d38f378ed2f103ac0a6768df830740c6835c4651921026bc363139ebc1cad8e6eee402507d2b4874f5450585f1e6a1cd30a63ecdfc9dc53ae
Description: You do flyer''s too? Yes, please!
Bid amount (BTC): 0.1
Job ID: 6g0j1m22lec5btt8b9t7
-----BEGIN SIGNATURE-----
1CptxARjqcfkVwGFSjR82zmPT8YtRMubub
IP4pFlJpPEyXHRtHnvm7UPNpF1VE0Puzfi+nuYorqEo2ZT+u87e0QXwNyNJC7SrlshO1iB59XEDjCQiSL4uGjxI=
-----END BITCOIN SIGNED MESSAGE-----','1HZwkjkeaoZfTSaJxDw6aKkxp45agDiEzN',1);
CREATE TABLE wallet (
    address varchar(64) primary key,
    contact varchar(256),
    owner varchar(64)
);
CREATE TABLE sale (
    id integer primary key,
    owner varchar(64),
    created text,
    amount integer,
    term integer,
    contact varchar(255),
    price integer,
    bytes_used integer,
    foreign key(owner) references owner(address)
);
INSERT INTO "sale" VALUES(1,'1HZwkjkeaoZfTSaJxDw6aKkxp45agDiEzN','2016-01-14 02:31:24',1,30,'bob@example.com',0,7441);
INSERT INTO "sale" VALUES(2,'1Djp4Siv5iLJUgXq5peWCDcHVWV1Mv3opc','2016-01-14 02:37:16',1,30,'alice@example.com',0,0);
INSERT INTO "sale" VALUES(3,'1M6DBU6LoaskwWxfpqaaZ1Z85nsixM97Tc','2016-01-14 02:39:12',1,30,'charlie@example.com',0,0);
CREATE TABLE log (
    created text,
    ip varchar(45),  /* max length of ipv6 address */
    action varchar(10),
    bytes integer,
    owner varchar(64),
    message text,
    foreign key(owner) references owner(address)
);
COMMIT;
