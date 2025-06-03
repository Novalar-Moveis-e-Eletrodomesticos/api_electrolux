WITH processosvenda AS (
  SELECT p.idprocesso FROM glb.processo p
  JOIN LATERAL (SELECT pp_1.idprocessocomposto FROM glb.processocomposto pp_1 WHERE pp_1.idprocesso = p.idprocesso) pp ON true
  JOIN LATERAL ( SELECT p1_1.idoperacao FROM glb.processo p1_1 WHERE p1_1.idprocesso = pp.idprocessocomposto) p1 ON true
  WHERE p1.idoperacao = 102010
),

vendas AS (
  SELECT 
    DISTINCT 
    'VENDA' AS tipo,pmi.idfilial,pmi.datamovimento,pv.idcnpj_cpf,ib.iditembase,ib.idpedidovenda,ib.idlocalsaldo,
        ib.idproduto,ib.idgradex,ib.idgradey,
        ib.idproduto||'.'||ib.idgradex||'.'||ib.idgradey AS chave,ib.idoperacaoproduto,ib.idvendedor,ib.quantidade,ib.totalpresente,ib.totalfuturo,ib.totalprecocusto,
        ib.totaldesejadopresente,to_char(pmi.datamovimento, 'MM/YYYY') AS mes_ano,
        ib.idprocessomestre
  FROM rst.pedidovendamovimentoitem pmi
  JOIN LATERAL (
    SELECT 
      ib_1.iditembase,ib_1.idpedidovenda,ib_1.idprocessomestre,ib_1.idlocalsaldo,
      ib_1.idproduto,ib_1.idgradex,ib_1.idgradey,ib_1.quantidade,ib_1.totalpresente,
      ib_1.totalfuturo,ib_1.totalprecocusto,ib_1.totaldesejadopresente,ib_1.idvendedor,ib_1.idoperacaoproduto
    FROM rst.itembase ib_1
    WHERE ib_1.idfilial = pmi.idfilial AND ib_1.iditembase = pmi.iditembase
  ) ib ON true
  JOIN LATERAL (SELECT pv_1.idcnpj_cpf FROM rst.pedidovenda pv_1 WHERE pv_1.idfilial = pmi.idfilial AND pv_1.idpedidovenda = pmi.idpedidovenda) pv ON true
  JOIN LATERAL (SELECT procv_1.idprocesso FROM processosvenda procv_1 WHERE procv_1.idprocesso = ib.idprocessomestre) procv ON true
  WHERE pmi.idsituacaopedidovenda = 3 AND pmi.datamovimento BETWEEN :data_ini AND :data_fin AND pmi.idfilial = ANY(:filial)
),

devolucao AS (
  SELECT 
    DISTINCT 
    'DEVOLUÇÃO' AS tipo,pmi.idfilial,pmi.datamovimento,pv.idcnpj_cpf,ib.iditembase,ib.idpedidovenda,ib.idlocalsaldo,
        ib.idproduto,ib.idgradex,ib.idgradey,
        ib.idproduto||'.'||ib.idgradex||'.'||ib.idgradey AS chave,ib.idoperacaoproduto,ib.idvendedor,pmi.quantidade * -1 AS quantidade,
        pmi.quantidade * (ib.totalpresente / ib.quantidade) * -1 AS totalpresente,
        pmi.quantidade * (ib.totalfuturo / ib.quantidade) * -1 AS totalfuturo,
        pmi.quantidade * (ib.totalprecocusto / ib.quantidade) * -1 AS totalprecocusto,
        pmi.quantidade * (ib.totaldesejadopresente / ib.quantidade) * -1 AS totaldesejadopresente,
        to_char(pmi.datamovimento, 'MM/YYYY') AS mes_ano,
        ib.idprocessomestre
  FROM rst.pedidovendamovimentoitem pmi
  JOIN LATERAL (
      SELECT 
        ib_1.iditembase,ib_1.idpedidovenda,ib_1.idprocessomestre,ib_1.idlocalsaldo,
        ib_1.idproduto,ib_1.idgradex,ib_1.idgradey,ib_1.quantidade,ib_1.totalpresente,
        ib_1.totalfuturo,ib_1.totalprecocusto,ib_1.totaldesejadopresente,ib_1.idvendedor,ib_1.idoperacaoproduto
      FROM rst.itembase ib_1
      WHERE ib_1.idfilial = pmi.idfilial AND ib_1.iditembase = pmi.iditembase
  ) ib ON true
  JOIN LATERAL (SELECT pv_1.idcnpj_cpf FROM rst.pedidovenda pv_1 WHERE pv_1.idfilial = pmi.idfilial AND pv_1.idpedidovenda = pmi.idpedidovenda) pv ON true
  JOIN LATERAL (SELECT procv_1.idprocesso FROM processosvenda procv_1 WHERE procv_1.idprocesso = ib.idprocessomestre) procv ON true
  WHERE pmi.idsituacaopedidovenda = 5 AND pmi.datamovimento BETWEEN :data_ini AND :data_fin AND pmi.idfilial = ANY(:filial)
),

vendas_e_devolucao AS (
SELECT * FROM vendas
UNION ALL
SELECT * FROM devolucao
)

SELECT
    vd.datamovimento AS data_sell_out,
    pe.cnpj_cpf,
    CASE
        WHEN vd.idprocessomestre = 9700 THEN 'online'
        ELSE 'offline'
    END AS tipo_cnpj,
    pgg.gtin AS EAN,
    SUM(vd.quantidade) AS quantidade,
    SUM(ps.saldo) AS estoque
FROM vendas_e_devolucao vd
INNER JOIN glb.filial f on vd.idfilial = f.idfilial
INNER JOIN glb.pessoa pe on f.idcnpj_cpf = pe.idcnpj_cpf
JOIN LATERAL (
    SELECT
        p.idmarca,m."descricao" AS marca,
        p.idproduto,pg.idgradex,pg.idgradey,
        p.idproduto||'.'||pg.idgradex||'.'||pg.idgradey AS chave,
        p.descricao||', '||gx.descricao||', '||gy."descricao" AS descricao_sku,
        pg.codigobarra,pg.codigofabricante
    FROM glb.produto p
    JOIN glb.produtograde pg on p.idproduto = pg.idproduto
    JOIN glb.gradex gx on pg.idgradex = gx.idgradex
    JOIN glb.gradey gy on pg.idgradey = gy.idgradey
    JOIN glb.marca m on p.idmarca = m.idmarca
    WHERE p.idproduto = vd.idproduto AND pg.idgradex = vd.idgradex AND pg.idgradey = vd.idgradey
    AND p.idproduto||'.'||pg.idgradex||'.'||pg.idgradey = vd.chave
) p ON TRUE
JOIN LATERAL (
    SELECT
        DISTINCT ON (ib.idfilial, sp.idsetorproduto, ib.idproduto,ib.idgradex,ib.idgradey,ib.idlocalsaldo)
        ib.idfilial,sp.descricao as grupo,ib.idproduto,
        ib.idgradex,ib.idgradey,ib.quantidade,ib.totalcustomedio,
        ib.quantidade,ib.saldo,ib.totalcustomedio,ib.quantidade
    from rst.itembase ib
    left join glb.produto pd on (ib.idproduto = pd.idproduto)
    left join glb.produtograde pg on (pg.idproduto = ib.idproduto and pg.idgradex = ib.idgradex and pg.idgradey = ib.idgradey)
    LEFT JOIN glb.setorproduto sp ON sp.idsetorproduto = pg.idsetorproduto     
    where ib.idfilial = ANY(:filial) and ib.datamovimento <= :data_fin and ib.idoperacaoproduto > 0
    and ib.idlocalsaldo = ANY(:idlocalsaldo) AND pd.idmarca = p.idmarca AND ib.idproduto = vd.idproduto
    AND ib.idgradex = vd.idgradex AND ib.idgradey = vd.idgradey AND ib.idproduto||'.'||ib.idgradex||'.'||ib.idgradey = vd.chave
    order by ib.idfilial, sp.idsetorproduto, ib.idproduto, ib.idgradex, ib.idgradey, ib.idlocalsaldo, ib.datamovimento desc, ib.idmovimento desc, ib.iditembase desc
) ps ON TRUE
JOIN glb.produtogradegtin pgg ON vd.idproduto = pgg.idproduto AND vd.idgradex = pgg.idgradex AND vd.idgradey = pgg.idgradey AND pgg.padrao = 1
WHERE p.idmarca = :marca
GROUP BY 1,2,3,4