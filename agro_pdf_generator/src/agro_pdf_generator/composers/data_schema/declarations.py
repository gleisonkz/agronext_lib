def build_declarations(is_quotation: bool = False):
    quotation_declarations_and_commitments = """
    <p>Eu, na qualidade de proponente, declaro para todos os fins legais que:</p>

<p><strong>A) Veracidade das informações e natureza do risco</strong></p>

<p><strong>Declaro</strong>, sob minha responsabilidade, que <strong>não tenho conhecimento</strong> de que o risco desta proposta <strong>já tenha ocorrido</strong> ou seja impossível de ocorrer e que todas as <strong>informações prestadas</strong> são <strong>verdadeiras</strong>, <strong>completas</strong> e <strong>atualizadas</strong>.</p>

<p><strong>B) Interesse legítimo e vínculo com o objeto</strong></p>

<p><strong>Reconheço</strong> que o <strong>interesse segurado</strong> decorre de <strong>vínculo jurídico ou econômico direto</strong> com o objeto do seguro (por exemplo: <strong>propriedade</strong>, <strong>posse</strong>, <strong>uso</strong>, <strong>responsabilidade legal</strong> ou <strong>obrigação contratual</strong>), sendo esse vínculo <strong>essencial à validade do contrato</strong>.</p>

<p><strong>C) Dever de comunicar alterações relevantes</strong></p>
<p><strong>Comprometo-me a informar imediatamente</strong> à seguradora <strong>qualquer alteração relevante</strong> que afete o <strong>interesse legítimo</strong>, a <strong>qualificação do(s) beneficiário(s)</strong> ou a <strong>estrutura contratual</strong>, ciente de minha <strong>responsabilidade civil e penal</strong>.</p>

<p><strong>D) Ciência das consequências por omissão ou má-fé</strong></p>

<p>Estou ciente de que:</p>
<ul>
<li>se houver <strong>omissão dolosa</strong> (intencional), <strong>perco o direito à indenização</strong> e posso ter de <strong>ressarcir despesas</strong> à seguradora;</li>
<li>se houver <strong>omissão culposa</strong> (sem intenção), a <strong>cobertura poderá ser reduzida proporcionalmente</strong>;</li>
<li>se os fatos omitidos <strong>tornarem a cobertura inviável</strong> ou <strong>incompatível</strong> com o contrato, este <strong>poderá ser cancelado</strong>.</li>
</ul>

<p><strong>E) Compromisso com Direitos Humanos e Idoneidade</strong></p>

<p>Declaro, sob minha responsabilidade, que nem eu, nem o(s) beneficiário(s), nem quaisquer terceiros envolvidos na presente proposta de seguro: (i) estamos incluídos em listas oficiais de trabalho escravo, infantil ou em condições análogas à escravidão; (ii) constamos em listas de sanções nacionais ou internacionais, incluindo, mas não se limitando a, ONU, OFAC, União Europeia ou Reino Unido; (iii) fomos condenados por crimes relacionados à lavagem de dinheiro, financiamento ao terrorismo ou infrações correlatas.</p>

<p>Estou ciente de que a falsidade ou omissão de qualquer dessas informações implicará a recusa da proposta pela Seguradora. Caso tais situações sejam identificadas durante a vigência da apólice, esta será cancelada de pleno direito.</p>

<p><strong>F) Formação e Informação Prévia</strong></p>

<p>Confirmo que esta proposta foi feita de forma voluntária, por mim ou por um representante autorizado. Os meus dados de contato (endereço, telefone e e-mail) são corretos e usados para comunicações da seguradora. Comprometo-me a mantê-los atualizados, pois, se não fizer isso, qualquer aviso enviado para esses contatos será considerado recebido.</p>

<p>Também confirmo que recebi todas as informações importantes para entender o contrato e as consequências de não informar corretamente os dados. Sou responsável por garantir que tudo o que informei é verdadeiro e completo. Respondi ao questionário de risco, quando necessário, com base no que sei, de forma clara e atualizada.</p>

<p>Tenho ciência dos anexos a esta Proposta, <strong>CUJAS CÓPIAS RECEBI NO ATO DA SUA ASSINATURA, ACEITANDO-OS NA ÍNTEGRA</strong>.</p>

<p>Se o seguro exigir informações contínuas (como averbações), sei que deixar de informar dados importantes pode fazer com que eu perca a cobertura, mesmo depois de um sinistro. Se a omissão não for intencional, vou pagar a diferença do prêmio e provar que agi de boa-fé.</p>

<p>Reconheço ainda que o corretor de seguros pode me representar, na forma da lei.</p>

<p><strong>G) Conhecimento do Contrato e dos Riscos Excluídos</strong></p>

<p>Declaro que li e compreendi as Condições Contratuais, conforme indicado no item “Avisos Importantes ao Proponente”, incluindo os riscos excluídos. Reconheço que a ausência de cobertura para tais riscos não configura falha contratual por parte da Seguradora.</p>

<p>Tenho ciência de que não terei direito a indenização se estiver em atraso no pagamento do prêmio, se o sinistro ocorrer antes da quitação das parcelas vencidas e não pagas (Art. 763 do Código Civil).</p>

<p><strong>H) Declaração sobre Interesse Legítimo, Conhecimento do Risco e Veracidade das Informações</strong></p>

<p>Estou contratando este seguro para proteger algo que me interessa ou que interessa a outra pessoa. Tenho ligação com o que está sendo segurado (como dono, responsável ou usuário).</p>
"""
    proposal_declarations_and_commitments = """
<p>Eu, na qualidade de proponente, declaro para todos os fins legais que:</p>

<p><strong>A) Veracidade das informações e natureza do risco</strong></p>

<p><strong>Declaro</strong>, sob minha responsabilidade, que <strong>não tenho conhecimento</strong> de que o risco desta proposta <strong>já tenha ocorrido</strong> ou seja impossível de ocorrer e que todas as <strong>informações prestadas</strong> são <strong>verdadeiras</strong>, <strong>completas</strong> e <strong>atualizadas</strong>.</p>

<p><strong>B) Interesse legítimo e vínculo com o objeto</strong></p>

<p><strong>Reconheço</strong> que o <strong>interesse segurado</strong> decorre de <strong>vínculo jurídico ou econômico direto</strong> com o objeto do seguro (por exemplo: <strong>propriedade</strong>, <strong>posse</strong>, <strong>uso</strong>, <strong>responsabilidade legal</strong> ou <strong>obrigação contratual</strong>), sendo esse vínculo <strong>essencial à validade do contrato</strong>.</p>

<p><strong>C) Dever de comunicar alterações relevantes</strong></p>
<p><strong>Comprometo-me a informar imediatamente</strong> à seguradora <strong>qualquer alteração relevante</strong> que afete o <strong>interesse legítimo</strong>, a <strong>qualificação do(s) beneficiário(s)</strong> ou a <strong>estrutura contratual</strong>, ciente de minha <strong>responsabilidade civil e penal</strong>.</p>

<p><strong>D) Ciência das consequências por omissão ou má-fé</strong></p>

<p>Estou ciente de que:</p>
<ul>
<li>se houver <strong>omissão dolosa</strong> (intencional), <strong>perco o direito à indenização</strong> e posso ter de <strong>ressarcir despesas</strong> à seguradora;</li>
<li>se houver <strong>omissão culposa</strong> (sem intenção), a <strong>cobertura poderá ser reduzida proporcionalmente</strong>;</li>
<li>se os fatos omitidos <strong>tornarem a cobertura inviável</strong> ou <strong>incompatível</strong> com o contrato, este <strong>poderá ser cancelado</strong>.</li>
</ul>

<p><strong>E) Compromisso com Direitos Humanos e Idoneidade</strong></p>

<p>Declaro, sob minha responsabilidade, que nem eu, nem o(s) beneficiário(s), nem quaisquer terceiros envolvidos na presente proposta de seguro: (i) estamos incluídos em listas oficiais de trabalho escravo, infantil ou em condições análogas à escravidão; (ii) constamos em listas de sanções nacionais ou internacionais, incluindo, mas não se limitando a, ONU, OFAC, União Europeia ou Reino Unido; (iii) fomos condenados por crimes relacionados à lavagem de dinheiro, financiamento ao terrorismo ou infrações correlatas.</p>

<p>Estou ciente de que a falsidade ou omissão de qualquer dessas informações implicará a recusa da proposta pela Seguradora. Caso tais situações sejam identificadas durante a vigência da apólice, esta será cancelada de pleno direito.</p>

<p><strong>F) Formação e Informação Prévia</strong></p>

<p>Confirmo que esta proposta foi feita de forma voluntária, por mim ou por um representante autorizado. Os meus dados de contato (endereço, telefone e e-mail) são corretos e usados para comunicações da seguradora. Comprometo-me a mantê-los atualizados, pois, se não fizer isso, qualquer aviso enviado para esses contatos será considerado recebido.</p>

<p>Também confirmo que recebi todas as informações importantes para entender o contrato e as consequências de não informar corretamente os dados. Sou responsável por garantir que tudo o que informei é verdadeiro e completo. Respondi ao questionário de risco, quando necessário, com base no que sei, de forma clara e atualizada.</p>

<p>Tenho ciência dos anexos a esta Proposta, <strong>CUJAS CÓPIAS RECEBI NO ATO DA SUA ASSINATURA, ACEITANDO-OS NA ÍNTEGRA</strong>.</p>

<p>Se o seguro exigir informações contínuas (como averbações), sei que deixar de informar dados importantes pode fazer com que eu perca a cobertura, mesmo depois de um sinistro. Se a omissão não for intencional, vou pagar a diferença do prêmio e provar que agi de boa-fé.</p>

<p>Reconheço ainda que o corretor de seguros pode me representar, na forma da lei.</p>

<p><strong>G) Conhecimento do Contrato e dos Riscos Excluídos</strong></p>

<p>Declaro que li e compreendi as Condições Contratuais, conforme indicado no item “Avisos Importantes ao Proponente”, incluindo os riscos excluídos. Reconheço que a ausência de cobertura para tais riscos não configura falha contratual por parte da Seguradora.</p>

<p>Tenho ciência de que não terei direito a indenização se estiver em atraso no pagamento do prêmio, se o sinistro ocorrer antes da quitação das parcelas vencidas e não pagas (Art. 763 do Código Civil).</p>

<p><strong>H) Declaração sobre Interesse Legítimo, Conhecimento do Risco e Veracidade das Informações</strong></p>

<p>Estou contratando este seguro para proteger algo que me interessa ou que interessa a outra pessoa. Tenho ligação com o que está sendo segurado (como dono, responsável ou usuário).</p>

<p><strong>Confirmo que: (i) o risco ainda não aconteceu; e (ii) as informações que dei são verdadeiras.</strong></p>

<p><strong>Se eu omitir/esconder algo: (i) de propósito: posso perder o direito ao seguro e ter que devolver o que recebi; (ii) sem querer: o seguro pode cobrir menos ou ser cancelado. Prometo avisar a seguradora se algo mudar que afete o seguro.</strong></p>

<p><strong>I) Declaração sobre Beneficiários do Seguro</strong></p>

<p>Os beneficiários que indiquei estão de acordo com a lei e têm um motivo legítimo para serem incluídos no seguro.</p>

<p><strong>Declaro que: (i) a escolha foi feita corretamente, sem problemas legais; (ii) existe uma relação que justifica essa indicação; (iii) não há fraude ou má intenção.</strong></p>

<p><strong>Me comprometo a avisar a seguradora se algo mudar que afete os beneficiários ou o motivo pelo qual foram indicados.</strong></p>

<p><strong>J) Cobertura Provisória</strong></p>

<p>Solicito a cobertura provisória e autorizo o pagamento antecipado do prêmio. Em caso de recusa da proposta, a seguradora deverá comunicar expressamente sua decisão e reembolsar integralmente o valor pago, exceto se houver cobertura efetiva, hipótese em que poderá haver retenção proporcional ao período de vigência.</p>

<p><strong>K) Declarações sobre os Programas de Subvenção</strong></p>

<p><strong>DECLARO</strong> que tomei ciência das Condições dos Programas de Subvenção ao Prêmio do Seguro dos Governos Federal e Estadual e ESTOU DE ACORDO COM SUAS CONDIÇÕES.</p>

<p>Se, por qualquer motivo, o Governo Federal e/ou Estadual não conceda subsídio ao prêmio para esta proposta, ME RESPONSABILIZO PELO CUSTO INTEGRAL DO SEGURO.</p>

<p><strong>AUTORIZO</strong> o uso de meio eletrônico pela Seguradora para o contato e envio de informações referentes ao seguro, inclusive envio de apólices e boletos.</p>
"""
    if is_quotation:
        return quotation_declarations_and_commitments
    return proposal_declarations_and_commitments