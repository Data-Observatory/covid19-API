# de https://www.influxdata.com/blog/getting-started-writing-data-to-influxdb/
# leemos los outputs de MinCiencia y los escribimos al formato nativo de influx:
# <measurement>[,<tag-key>=<tag-value>...] <field-key>=<field-value>[,<field2-key>=<field2-value>...] [unix-nano-timestamp]
# Prueba 1: measurement = cada campo; tags = region o rango etareo y sexo, y hay que convertir los timestamps
import sys

import pandas as pd
import unidecode
import time

GITHUB_REPO = 'https://raw.githubusercontent.com/MinCiencia/Datos-COVID19/master/output'

relevantCSVs = {
    'prod1': ('%s/producto1/Covid-19_std.csv' % GITHUB_REPO),
    'prod2': ('%s/producto6/bulk/data.csv' % GITHUB_REPO),
    # Prod 1
    'prod3': ('%s/producto3/CasosTotalesCumulativo_std.csv' % GITHUB_REPO),
    'prod4': ('%s/producto11/bulk/producto4.csv' % GITHUB_REPO),
    # Prod 5
    'prod5': ('%s/producto5/TotalesNacionales_std.csv' % GITHUB_REPO),
    'prod6': '',  # this is prod 2
    'prod7': ('%s/producto7/PCR_std.csv' % GITHUB_REPO),
    'prod8': ('%s/producto8/UCI_std.csv' % GITHUB_REPO),
    'prod9': ('%s/producto9/HospitalizadosUCIEtario_std.csv' % GITHUB_REPO),
    'prod10': ('%s/producto10/FallecidosEtario_std.csv' % GITHUB_REPO),
    'prod11': '',  # this is prod 4
    'prod12': '',  # this is prod 7
    'prod13': ('%s/producto13/CasosNuevosCumulativo_std.csv' % GITHUB_REPO),
    'prod14': ('%s/producto14/FallecidosCumulativo_std.csv' % GITHUB_REPO),
    #'prod15': ('%s/producto15/FechaInicioSintomasHistorico_std.csv' % GITHUB_REPO),
    # 'prod15.2': ('%s/producto15/SemanasEpidemiologicas.csv', % GITHUB_REPO),
    'prod16': ('%s/producto16/CasosGeneroEtario_std.csv' % GITHUB_REPO),
    'prod17': ('%s/producto17/PCREstablecimiento_std.csv' % GITHUB_REPO),
    'prod18': ('%s/producto18/TasaDeIncidencia_std.csv' % GITHUB_REPO),
    'prod19': ('%s/producto19/CasosActivosPorComuna_std.csv' % GITHUB_REPO),
    'prod20': ('%s/producto20/NumeroVentiladores_std.csv' % GITHUB_REPO),
    'prod21.1': ('%s/producto21/SintomasCasosConfirmados_std.csv' % GITHUB_REPO),
    'prod21.2': ('%s/producto21/SintomasHospitalizados_std.csv' % GITHUB_REPO),
    'prod22.1': ('%s/producto22/HospitalizadosEtario_Acumulado_std.csv' % GITHUB_REPO),
    'prod22.2': ('%s/producto22/HospitalizadosUCI_Acumulado_std.csv' % GITHUB_REPO),
    'prod23': ('%s/producto23/PacientesCriticos_std.csv' % GITHUB_REPO),
    'prod24': ('%s/producto24/CamasHospital_Diario_std.csv' % GITHUB_REPO),
    'prod25': ('%s/producto25/CasosActualesPorComuna_std.csv' % GITHUB_REPO),
    'prod26': ('%s/producto26/CasosNuevosConSintomas_std.csv' % GITHUB_REPO),
    'prod27': ('%s/producto27/CasosNuevosSinSintomas_std.csv' % GITHUB_REPO),
    'prod28': ('%s/producto28/FechaInicioSintomas_reportadosSEREMIHistorico_std.csv' % GITHUB_REPO),
    'prod29': '',  # geo product
    'prod30': ('%s/producto30/PacientesVMI_std.csv' % GITHUB_REPO),
    'prod31': ('%s/producto31/Nacimientos_std.csv' % GITHUB_REPO),
    'prod32': ('%s/producto32/Defunciones_std.csv' % GITHUB_REPO),
    'prod33': ('%s/producto33/IndiceDeMovilidad_std.csv' % GITHUB_REPO),
    'prod34': '',  # geo product
    'prod35': ('%s/producto35/Comorbilidad_std.csv' % GITHUB_REPO),
    'prod36': ('%s/producto36/ResidenciasSanitarias_std.csv' % GITHUB_REPO),
    'prod37': ('%s/producto37/Defunciones_deis_std.csv' % GITHUB_REPO),
    'prod38': ('%s/producto38/CasosFallecidosPorComuna_std.csv' % GITHUB_REPO),
    'prod39': ('%s/producto39/NotificacionInicioSintomas_std.csv' % GITHUB_REPO),
    'prod40': ('%s/producto40/TransporteAereo_std.csv' % GITHUB_REPO),
    'prod41.1': ('%s/producto41/BIPTotal_std.csv' % GITHUB_REPO),
    'prod41.2': ('%s/producto41/BIPComuna_std.csv' % GITHUB_REPO),
    'prod42': ('%s/producto42/ViajesComunas_std.csv' % GITHUB_REPO),
    'prod44': ('%s/producto44/EgresosHospitalarios_std.csv' % GITHUB_REPO),
    # 'prod45_1': ('%s/producto45/CasosConfirmadosPorComunaHistorico_std.csv' % GITHUB_REPO),
    # 'prod45_2': ('%s/producto45/CasosNoNotificadosPorComunaHistorico_std.csv' % GITHUB_REPO),
    # 'prod45_3': ('%s/producto45/CasosProbablesPorComunaHistorico_std.csv' % GITHUB_REPO),
    'prod46': ('%s/producto46/activos_vs_recuperados_std.csv' % GITHUB_REPO),
    'prod47': ('%s/producto47/MediaMovil_std.csv' % GITHUB_REPO),
    'prod48': ('%s/producto48/SOCHIMI_std.csv' % GITHUB_REPO),
    'prod49': ('%s/producto49/Positividad_Diaria_Media_std.csv' % GITHUB_REPO),
    'prod50': ('%s/producto50/DefuncionesDEISPorComuna_std.csv' % GITHUB_REPO),
    'prod51': ('%s/producto51/ISCI_std.csv' % GITHUB_REPO),
    'prod52': ('%s/producto52/Camas_UCI_std.csv' % GITHUB_REPO),
}


def file_writer(path, lines):
    the_file = open(path, 'w')
    header = ['# DML', '# CONTEXT-DATABASE: covid19']
    for line in header:
        the_file.write("%s\n" % line)
    for item in lines:
        the_file.write("%s\n" % item)


def prod1_to_line(df1, path):
    lines = []
    for d in range(len(df1)):
        lines.append('Casos_confirmados_comunal,'
                     # TAGS are used to check if measurements are the same
                     + 'Region="' + unidecode.unidecode(str(df1['Region'][d]).replace(' ', '_')) + '",'
                     + 'Codigo_region="' + str(df1['Codigo region'][d]) + '",'
                     + 'Comuna="' + unidecode.unidecode(str(df1['Comuna'][d]).replace(' ', '_')) + '",'
                     + 'Codigo_comuna="' + str(df1['Codigo comuna'][d]) + '"'
                     + ' '
                     # Fields

                     + 'Poblacion=' + str(df1['Poblacion'][d]) + ","
                     + 'Casos_confirmados=' + str(df1['Casos confirmados'][d])
                     + ' '
                     + str(pd.to_datetime(df1["Fecha"][d]).value)
                     )
    file_writer(path, lines)


def prod2_to_line(df2, path):
    # Poblacion,Casos Confirmados,Fecha,Region ID,Region,Provincia ID,Provincia,Comuna ID,Comuna,Tasa
    lines = []
    df2.replace(to_replace='-', value=0, regex=True, inplace=True)
    for d in range(len(df2)):
        lines.append('Tasa_de_incidencia,'
                     # TAGS are used to check if measurements are the same
                     + 'Region="' + unidecode.unidecode(str(df2['Region'][d]).replace(' ', '_')) + '",'
                     + 'Codigo_region="' + str(df2['Region ID'][d]) + '",'
                     + 'Comuna="' + unidecode.unidecode(str(df2['Comuna'][d]).replace(' ', '_')) + '",'
                     + 'Codigo_comuna="' + str(df2['Comuna ID'][d]) + '"'
                     + ' '
                     # Fields
                     + 'Poblacion=' + str(df2['Poblacion'][d]) + ","
                     + 'Tasa=' + str(df2['Tasa'][d])
                     + ' '
                     + str(pd.to_datetime(df2["Fecha"][d]).value)
                     )
    file_writer(path, lines)


def prod3_to_line(df3, path):
    lines = []
    for d in range(len(df3)):
        lines.append('Casos_acumulados_regional,'
                     # TAGS are used to check if measurements are the same
                     + 'Region="' + unidecode.unidecode(str(df3['Region'][d]).replace(' ', '_')) + '"'
                     + ' '
                     # Fields
                     + 'Casos_acumulados=' + str(df3['Total'][d])
                     + ' '
                     + str(pd.to_datetime(df3["Fecha"][d]).value)
                     )
    file_writer(path, lines)


def prod5_to_line(df5, path):
    lines = []
    for d in range(len(df5)):
        lines.append('Totales_nacionales,'
                     # TAGS are used to check if measurements are the same
                     + 'Serie="' + unidecode.unidecode(str(df5['Dato'][d]).replace(' ', '_')) + '"'
                     + ' '
                     # Fields
                     + 'Total=' + str(df5['Total'][d])
                     + ' '
                     + str(pd.to_datetime(df5["Fecha"][d]).value)
                     )
    file_writer(path, lines)


def prod7_to_line(df7, path):
    lines = []
    for d in range(len(df7)):
        lines.append('PCR_Regional,'
                     # TAGS are used to check if measurements are the same
                     + 'Region="' + unidecode.unidecode(str(df7['Region'][d]).replace(' ', '_')) + '",'
                     + 'Codigo_region="' + str(df7['Codigo region'][d]) + '"'
                     + ' '
                     # Fields
                     + 'Total=' + str(df7['numero'][d]).replace('-', '0')
                     + ' '
                     + str(pd.to_datetime(df7["fecha"][d]).value)
                     )
    file_writer(path, lines)


def prod8_to_line(df8, path):
    lines = []
    for d in range(len(df8)):
        lines.append('UCI_Regional,'
                     # TAGS are used to check if measurements are the same
                     + 'Region="' + unidecode.unidecode(str(df8['Region'][d]).replace(' ', '_')) + '",'
                     + 'Codigo_region="' + str(df8['Codigo region'][d]) + '"'
                     + ' '
                     # Fields
                     + 'Total=' + str(df8['numero'][d]).replace('-', '0')
                     + ' '
                     + str(pd.to_datetime(df8["fecha"][d]).value)
                     )
    file_writer(path, lines)


def prod9_to_line(df9, path):
    lines = []
    df9 = df9.replace('<=', 'menor que ', regex=True)
    df9 = df9.replace('>=', 'mayor que ', regex=True)
    for d in range(len(df9)):
        lines.append('UCI_Etario,'
                     # TAGS are used to check if measurements are the same
                     + 'Grupo_de_edad="' + unidecode.unidecode(str(df9['Grupo de edad'][d]).replace(' ', '_')) + '"'
                     + ' '
                     # Fields
                     + 'Total=' + str(df9['Casos confirmados'][d]).replace('-', '0')
                     + ' '
                     + str(pd.to_datetime(df9["fecha"][d]).value)
                     )
    file_writer(path, lines)


def prod10_to_line(df10, path):
    lines = []
    df10 = df10.replace('<=', 'menor que ', regex=True)
    df10 = df10.replace('>=', 'mayor que ', regex=True)
    for d in range(len(df10)):
        lines.append('Fallecidos_Etario,'
                     # TAGS are used to check if measurements are the same
                     + 'Grupo_de_edad="' + unidecode.unidecode(str(df10['Grupo de edad'][d]).replace(' ', '_')) + '"'
                     + ' '
                     # Fields
                     + 'Total=' + str(df10['Casos confirmados'][d]).replace('-', '0')
                     + ' '
                     + str(pd.to_datetime(df10["fecha"][d]).value)
                     )
    file_writer(path, lines)


def prod13_to_line(df13, path):
    lines = []
    df13 = df13.replace('<=', 'menor que ', regex=True)
    df13 = df13.replace('>=', 'mayor que ', regex=True)
    for d in range(len(df13)):
        lines.append('Casos_nuevos_cumulativo_regional,'
                     # TAGS are used to check if measurements are the same
                     + 'Region="' + unidecode.unidecode(str(df13['Region'][d]).replace(' ', '_')) + '"'
                     + ' '
                     # Fields
                     + 'Total=' + str(df13['Total'][d]).replace('-', '0')
                     + ' '
                     + str(pd.to_datetime(df13["Fecha"][d]).value)
                     )
    file_writer(path, lines)


def prod14_to_line(df14, path):
    lines = []
    df14 = df14.replace('<=', 'menor que ', regex=True)
    df14 = df14.replace('>=', 'mayor que ', regex=True)
    for d in range(len(df14)):
        lines.append('Fallecidos_cumulativo_regional,'
                     # TAGS are used to check if measurements are the same
                     + 'Region="' + unidecode.unidecode(str(df14['Region'][d]).replace(' ', '_')) + '"'
                     + ' '
                     # Fields
                     + 'Total=' + str(df14['Total'][d]).replace('-', '0')
                     + ' '
                     + str(pd.to_datetime(df14["Fecha"][d]).value)
                     )
    file_writer(path, lines)


def prod15_to_line(df15, path):
    lines = []
    df2 = pd.read_csv(
        '%s/producto15/SemanasEpidemiologicas.csv' % GITHUB_REPO)
    for d in range(len(df15)):
        lines.append('Inicio_sintomas_comunal,'
                     # TAGS are used to check if measurements are the same
                     + 'Region="' + unidecode.unidecode(str(df15['Region'][d]).replace(' ', '_')) + '",'
                     + 'Codigo_region="' + str(df15['Codigo region'][d]) + '",'
                     + 'Comuna="' + unidecode.unidecode(str(df15['Comuna'][d]).replace(' ', '_')) + '",'
                     + 'Codigo_comuna="' + str(df15['Codigo comuna'][d]) + '",'
                     + 'Publicacion="' + str(df15['Publicacion'][d]) + '"'
                     + ' '
                     # Fields
                     + 'Poblacion=' + str(df15['Poblacion'][d]) + ","
                     + 'Casos_confirmados=' + str(df15['Casos confirmados'][d])
                     + ' '
                     + str(pd.to_datetime(df2.loc[[0], df15["Semana Epidemiologica"][d]][0]).value)
                     )
    file_writer(path, lines)


def prod16_to_line(df16, path):
    lines = []
    df16 = df16.replace('<=', 'menor que ', regex=True)
    df16 = df16.replace('>=', 'mayor que ', regex=True)
    for d in range(len(df16)):
        lines.append('Casos_genero_Etario,'
                     # TAGS are used to check if measurements are the same
                     + 'Grupo_de_edad="' + unidecode.unidecode(str(df16['Grupo de edad'][d]).replace(' ', '_')) + '",'
                     + 'Sexo="' + unidecode.unidecode(str(df16['Sexo'][d]).replace(' ', '_')) + '"'
                     + ' '
                     # Fields
                     + 'Total=' + str(df16['Casos confirmados'][d]).replace('-', '0')
                     + ' '
                     + str(pd.to_datetime(df16["Fecha"][d]).value)
                     )
    file_writer(path, lines)


def prod17_to_line(df17, path):
    lines = []
    df17 = df17.replace('<=', 'menor que ', regex=True)
    df17 = df17.replace('>=', 'mayor que ', regex=True)
    for d in range(len(df17)):
        lines.append('PCR_tipo_establecimiento,'
                     # TAGS are used to check if measurements are the same
                     + 'Establecimiento="' + unidecode.unidecode(
            str(df17['Establecimiento'][d]).replace(' ', '_')) + '",'
                     + 'Examenes="' + unidecode.unidecode(str(df17['Examenes'][d]).replace(' ', '_')) + '"'
                     + ' '
                     # Fields
                     + 'Total=' + str(df17['Numero de PCR'][d]).replace('-', '0')
                     + ' '
                     + str(pd.to_datetime(df17["fecha"][d]).value)
                     )
    file_writer(path, lines)


def prod18_to_line(df18, path):
    lines = []
    for d in range(len(df18)):
        lines.append('Tasa_de_incidencia_comunal,'
                     # TAGS are used to check if measurements are the same
                     + 'Region="' + unidecode.unidecode(str(df18['Region'][d]).replace(' ', '_')) + '",'
                     + 'Codigo_region="' + str(df18['Codigo region'][d]) + '",'
                     + 'Comuna="' + unidecode.unidecode(str(df18['Comuna'][d]).replace(' ', '_')) + '",'
                     + 'Codigo_comuna="' + str(df18['Codigo comuna'][d]) + '"'
                     + ' '
                     # Fields

                     + 'Poblacion=' + str(df18['Poblacion'][d]) + ","
                     + 'Tasa_de_incidencia=' + str(df18['Tasa de incidencia'][d])
                     + ' '
                     + str(pd.to_datetime(df18["Fecha"][d]).value)
                     )
    file_writer(path, lines)


def prod19_to_line(df19, path):
    lines = []
    for d in range(len(df19)):
        lines.append('Casos_activos_comunal,'
                     # TAGS are used to check if measurements are the same
                     + 'Region="' + unidecode.unidecode(str(df19['Region'][d]).replace(' ', '_')) + '",'
                     + 'Codigo_region="' + str(df19['Codigo region'][d]) + '",'
                     + 'Comuna="' + unidecode.unidecode(str(df19['Comuna'][d]).replace(' ', '_')) + '",'
                     + 'Codigo_comuna="' + str(df19['Codigo comuna'][d]) + '"'
                     + ' '
                     # Fields

                     + 'Poblacion=' + str(df19['Poblacion'][d]) + ","
                     + 'Casos_activos=' + str(df19['Casos activos'][d])
                     + ' '
                     + str(pd.to_datetime(df19["Fecha"][d]).value)
                     )
    file_writer(path, lines)


def prod20_to_line(df20, path):
    lines = []
    df20 = df20.replace('<=', 'menor que ', regex=True)
    df20 = df20.replace('>=', 'mayor que ', regex=True)
    for d in range(len(df20)):
        lines.append('Ventiladores_nacional,'
                     # TAGS are used to check if measurements are the same
                     + 'Ventiladores="' + unidecode.unidecode(str(df20['Ventiladores'][d]).replace(' ', '_')) + '"'
                     + ' '
                     # Fields
                     + 'Total=' + str(df20['numero'][d]).replace('-', '0')
                     + ' '
                     + str(pd.to_datetime(df20["fecha"][d]).value)
                     )
    file_writer(path, lines)


def prod21_1_to_line(df211, path):
    lines = []
    df211 = df211.replace('<=', 'menor que ', regex=True)
    df211 = df211.replace('>=', 'mayor que ', regex=True)
    for d in range(len(df211)):
        lines.append('Sintomas_casos_confirmados,'
                     # TAGS are used to check if measurements are the same
                     + 'Sintomas="' + unidecode.unidecode(str(df211['Sintomas'][d]).replace(' ', '_')) + '"'
                     + ' '
                     # Fields
                     + 'Total=' + str(df211['numero'][d]).replace('-', '0')
                     + ' '
                     + str(pd.to_datetime(df211["fecha"][d]).value)
                     )
    file_writer(path, lines)


def prod21_2_to_line(df212, path):
    lines = []
    df212 = df212.replace('<=', 'menor que ', regex=True)
    df212 = df212.replace('>=', 'mayor que ', regex=True)
    for d in range(len(df212)):
        lines.append('Sintomas_hospitalizados,'
                     # TAGS are used to check if measurements are the same
                     + 'Sintomas="' + unidecode.unidecode(str(df212['Sintomas'][d]).replace(' ', '_')) + '"'
                     + ' '
                     # Fields
                     + 'Total=' + str(df212['numero'][d]).replace('-', '0')
                     + ' '
                     + str(pd.to_datetime(df212["fecha"][d]).value)
                     )
    file_writer(path, lines)


def prod22_1_to_line(df221, path):
    lines = []
    df221 = df221.replace('<=', 'menor que ', regex=True)
    df221 = df221.replace('>=', 'mayor que ', regex=True)
    for d in range(len(df221)):
        lines.append('Hospitalizados_etario,'
                     # TAGS are used to check if measurements are the same
                     + 'Grupo_de_edad="' + unidecode.unidecode(str(df221['Grupo de edad'][d]).replace(' ', '_')) + '",'
                     + 'Sexo="' + unidecode.unidecode(str(df221['Sexo'][d]).replace(' ', '_')) + '"'
                     + ' '
                     # Fields
                     + 'Total=' + str(df221['numero'][d]).replace('-', '0')
                     + ' '
                     + str(pd.to_datetime(df221["fecha"][d]).value)
                     )
    file_writer(path, lines)


def prod22_2_to_line(df222, path):
    lines = []
    df222 = df222.replace('<=', 'menor que ', regex=True)
    df222 = df222.replace('>=', 'mayor que ', regex=True)
    for d in range(len(df222)):
        lines.append('Hospitalizados_UCI_etario,'
                     # TAGS are used to check if measurements are the same
                     + 'Grupo_de_edad="' + unidecode.unidecode(str(df222['Grupo de edad'][d]).replace(' ', '_')) + '"'
                     + ' '
                     # Fields
                     + 'Total=' + str(df222['numero'][d]).replace('-', '0')
                     + ' '
                     + str(pd.to_datetime(df222["fecha"][d]).value)
                     )
    file_writer(path, lines)


def prod23_to_line(df23, path):
    lines = []
    df23 = df23.replace('<=', 'menor que ', regex=True)
    df23 = df23.replace('>=', 'mayor que ', regex=True)
    for d in range(len(df23)):
        lines.append('Pacientes_criticos'
                     # TAGS are used to check if measurements are the same
                     # + 'Pacientes_criticos="' + unidecode.unidecode(str(df['Sintomas'][d]).replace(' ', '_')) + '"'
                     + ' '
                     # Fields
                     + 'Total=' + str(df23['Casos confirmados'][d]).replace('-', '0')
                     + ' '
                     + str(pd.to_datetime(df23["fecha"][d]).value)
                     )
    file_writer(path, lines)


def prod24_to_line(df24, path):
    lines = []
    df24 = df24.replace('<=', 'menor que ', regex=True)
    df24 = df24.replace('>=', 'mayor que ', regex=True)
    for d in range(len(df24)):
        lines.append('Camas_hospital,'
                     # TAGS are used to check if measurements are the same
                     + 'Tipo_de_cama="' + unidecode.unidecode(str(df24['Tipo de cama'][d]).replace(' ', '_')) + '"'
                     + ' '
                     # Fields
                     + 'Total=' + str(df24['Casos confirmados'][d]).replace('-', '0')
                     + ' '
                     + str(pd.to_datetime(df24["fecha"][d]).value)
                     )
    file_writer(path, lines)


def prod25_to_line(df25, path):
    lines = []
    for d in range(len(df25)):
        lines.append('Casos_actuales_comunal,'
                     # TAGS are used to check if measurements are the same
                     + 'Region="' + unidecode.unidecode(str(df25['Region'][d]).replace(' ', '_')) + '",'
                     + 'Codigo_region="' + str(df25['Codigo region'][d]) + '",'
                     + 'Comuna="' + unidecode.unidecode(str(df25['Comuna'][d]).replace(' ', '_')) + '",'
                     + 'Codigo_comuna="' + str(df25['Codigo comuna'][d]) + '"'
                     + ' '
                     # Fields

                     + 'Poblacion=' + str(df25['Poblacion'][d]) + ","
                     + 'Casos_actuales=' + str(df25['Casos actuales'][d])
                     + ' '
                     + str(pd.to_datetime(df25["Fecha"][d]).value)
                     )
    file_writer(path, lines)


def prod26_to_line(df26, path):
    lines = []
    for d in range(len(df26)):
        lines.append('Casos_nuevos_con_sintomas_regional,'
                     # TAGS are used to check if measurements are the same
                     + 'Region="' + unidecode.unidecode(str(df26['Region'][d]).replace(' ', '_')) + '"'
                     + ' '
                     # Fields
                     + 'Casos=' + str(df26['Casos confirmados'][d])
                     + ' '
                     + str(pd.to_datetime(df26["Fecha"][d]).value)
                     )
    file_writer(path, lines)


def prod27_to_line(df27, path):
    lines = []
    for d in range(len(df27)):
        lines.append('Casos_nuevos_sin_sintomas_regional,'
                     # TAGS are used to check if measurements are the same
                     + 'Region="' + unidecode.unidecode(str(df27['Region'][d]).replace(' ', '_')) + '"'
                     + ' '
                     # Fields
                     + 'Casos=' + str(df27['Casos confirmados'][d])
                     + ' '
                     + str(pd.to_datetime(df27["Fecha"][d]).value)
                     )
    file_writer(path, lines)


def prod28_to_line(df28, path):
    lines = []
    df2 = pd.read_csv(
        '%s/producto15/SemanasEpidemiologicas.csv' % GITHUB_REPO)
    for d in range(len(df28)):
        lines.append('Inicio_sintomas_reportados,'
                     # TAGS are used to check if measurements are the same
                     + 'Region="' + unidecode.unidecode(str(df28['Region'][d]).replace(' ', '_')) + '",'
                     + 'Codigo_region="' + str(df28['Codigo region'][d]) + '",'
                     + 'Publicacion="' + str(df28['Publicacion'][d]) + '"'
                     + ' '
                     # Fields
                     + 'Casos_confirmados=' + str(df28['Casos confirmados'][d])
                     + ' '
                     + str(pd.to_datetime(df2.loc[[0], df28["Semana Epidemiologica"][d]][0]).value)
                     )
    file_writer(path, lines)


def prod30_to_line(df30, path):
    lines = []
    df30 = df30.replace('<=', 'menor que ', regex=True)
    df30 = df30.replace('>=', 'mayor que ', regex=True)
    for d in range(len(df30)):
        lines.append('Pacientes_VMI'
                     # TAGS are used to check if measurements are the same
                     # + 'Pacientes_criticos="' + unidecode.unidecode(str(df['Sintomas'][d]).replace(' ', '_')) + '"'
                     + ' '
                     # Fields
                     + 'Total=' + str(df30['Casos confirmados'][d]).replace('-', '0')
                     + ' '
                     + str(pd.to_datetime(df30["Fecha"][d]).value)
                     )
    file_writer(path, lines)


def prod31_to_line(df31, path):
    lines = []
    for d in range(len(df31)):
        lines.append('Nacimientos_comunal,'
                     # TAGS are used to check if measurements are the same
                     + 'Region="' + unidecode.unidecode(str(df31['Region'][d]).replace(' ', '_')) + '",'
                     + 'Codigo_region="' + str(df31['Codigo region'][d]) + '",'
                     + 'Comuna="' + unidecode.unidecode(str(df31['Comuna'][d]).replace(' ', '_')) + '",'
                     + 'Codigo_comuna="' + str(df31['Codigo comuna'][d]) + '"'
                     + ' '
                     # Fields
                     + 'Nacimientos=' + str(df31['Nacimientos'][d])
                     + ' '
                     + str(pd.to_datetime(df31["Fecha"][d]).value)
                     )
    file_writer(path, lines)


def prod32_to_line(df32, path):
    lines = []
    for d in range(len(df32)):
        lines.append('Defunciones_comunal,'
                     # TAGS are used to check if measurements are the same
                     + 'Region="' + unidecode.unidecode(str(df32['Region'][d]).replace(' ', '_')) + '",'
                     + 'Codigo_region="' + str(df32['Codigo region'][d]) + '",'
                     + 'Comuna="' + unidecode.unidecode(str(df32['Comuna'][d]).replace(' ', '_')) + '",'
                     + 'Codigo_comuna="' + str(df32['Codigo comuna'][d]) + '"'
                     + ' '
                     # Fields
                     + 'Defunciones=' + str(df32['Defunciones'][d])
                     + ' '
                     + str(pd.to_datetime(df32["Fecha"][d]).value)
                     )
    file_writer(path, lines)


def prod33_to_line(df33, path):
    lines = []
    # Region,Codigo region,Comuna,Codigo comuna,Superficie_km2,Poblacion,Fecha,variable,value
    for d in range(len(df33)):
        lines.append('Indice_de_movilidad,'
                     # TAGS are used to check if measurements are the same
                     + 'Region="' + unidecode.unidecode(str(df33['Region'][d]).replace(' ', '_')) + '",'
                     + 'Codigo_region="' + str(df33['Codigo region'][d]) + '",'
                     + 'Comuna="' + unidecode.unidecode(str(df33['Comuna'][d]).replace(' ', '_')) + '",'
                     + 'Codigo_comuna="' + str(df33['Codigo comuna'][d]) + '",'
                     + 'Serie="' + unidecode.unidecode(str(df33['variable'][d])) + '"'
                     + ' '
                     # Fields
                     + 'Poblacion=' + str(df33['Poblacion'][d]) + ","
                     + 'Superficie_km2=' + str(df33['Superficie_km2'][d]) + ","
                     + 'Indice=' + str(df33['value'][d])
                     + ' '
                     + str(pd.to_datetime(df33["Fecha"][d]).value)
                     )
    file_writer(path, lines)


def prod35_to_line(df35, path):
    lines = []
    for d in range(len(df35)):
        lines.append('Comorbilidad,'
                     # TAGS are used to check if measurements are the same
                     + 'Comorbilidad="' + unidecode.unidecode(str(df35['Comorbilidad'][d]).replace(' ', '_')) + '",'
                     + 'Hospitalizacion="' + unidecode.unidecode(
            str(df35['Hospitalización'][d]).replace(' ', '_')) + '"'
                     + ' '
                     # Fields
                     + 'Total=' + str(df35['Casos confirmados'][d]).replace('-', '0')
                     + ' '
                     + str(pd.to_datetime(df35["Fecha"][d]).value)
                     )
    file_writer(path, lines)


def prod36_to_line(df36, path):
    lines = []
    for d in range(len(df36)):
        lines.append('Residencias_sanitarias,'
                     # TAGS are used to check if measurements are the same
                     + 'Region="' + unidecode.unidecode(str(df36['Region'][d]).replace(' ', '_')) + '",'
                     + 'Categoria="' + unidecode.unidecode(str(df36['Categoria'][d]).replace(' ', '_')) + '"'
                     + ' '
                     # Fields
                     + 'Total=' + str(df36['Numero'][d]).replace('-', '0')
                     + ' '
                     + str(pd.to_datetime(df36["Fecha"][d]).value)
                     )
    file_writer(path, lines)


def prod37_to_line(df37, path):
    lines = []
    df37 = df37[df37['Fecha'] != 'en verificación']
    df37.reset_index(drop=True, inplace=True)

    for d in range(len(df37)):

        lines.append('Defunciones_deis,'
                     # TAGS are used to check if measurements are the same
                     + 'Publicacion="' + unidecode.unidecode(str(df37['Publicacion'][d]).replace(' ', '_')) + '",'
                     + 'Serie="' + unidecode.unidecode(str(df37['Serie'][d])) + '"'
                     + ' '
                     # Fields
                     + 'Total=' + str(df37['Numero defunciones'][d]).replace('-', '0')
                     + ' '
                     + str(pd.to_datetime(df37["Fecha"][d]).value)
                     )
    file_writer(path, lines)


def prod38_to_line(df38, path):
    lines = []
    # Region,Codigo region,Comuna,Codigo comuna,Superficie_km2,Poblacion,Fecha,variable,value
    for d in range(len(df38)):
        lines.append('Defunciones_comunales,'
                     # TAGS are used to check if measurements are the same
                     + 'Region="' + unidecode.unidecode(str(df38['Region'][d]).replace(' ', '_')) + '",'
                     + 'Codigo_region="' + str(df38['Codigo region'][d]) + '",'
                     + 'Comuna="' + unidecode.unidecode(str(df38['Comuna'][d]).replace(' ', '_')) + '",'
                     + 'Codigo_comuna="' + str(df38['Codigo comuna'][d]) + '"'
                     + ' '
                     # Fields
                     + 'Total=' + str(df38['Casos fallecidos'][d])
                     + ' '
                     + str(pd.to_datetime(df38["Fecha"][d]).value)
                     )
    file_writer(path, lines)


def prod39_to_line(df39, path):
    # Categoria, Serie, Fecha, Casos
    lines = []
    df39 = df39[df39['Fecha'] != 'sin fecha']
    df39.reset_index(drop=True, inplace=True)
    #print(df39)
    for d in range(len(df39)):
        lines.append('Notificacion_inicio_sintomas,'
                     # TAGS are used to check if measurements are the same
                     + 'Categoría="' + unidecode.unidecode(str(df39['Categoria'][d]).replace(' ', '_')) + '",'
                     + 'Serie="' + unidecode.unidecode(str(df39['Serie'][d]).replace(' ', '_')) + '"'
                     + ' '
                     # Fields
                     + 'Total=' + str(df39['Casos'][d])
                     + ' '
                     + str(pd.to_datetime(df39["Fecha"][d]).value)
                     )
    file_writer(path, lines)


def prod40_to_line(df40, path):
    lines = []
    for d in range(len(df40)):
        # Semana,Inicio_semana,Fin_semana,Cod_region_origen,Region_origen,Cod_region_destino,Region_destino,Origen,Destino,Operaciones,Pasajeros
        lines.append('Transporte_aereo,'
                     # TAGS are used to check if measurements are the same
                     + 'Cod_region_origen="' + str(df40['Cod_region_origen'][d]) + '",'
                     + 'Region_origen="' + unidecode.unidecode(str(df40['Region_origen'][d]).replace(' ', '_')) + '",'
                     + 'Cod_region_destino="' + str(df40['Cod_region_destino'][d]) + '",'
                     + 'Region_destino="' + unidecode.unidecode(str(df40['Region_destino'][d]).replace(' ', '_')) + '",'
                     + 'Origen="' + unidecode.unidecode(str(df40['Origen'][d]).replace(' ', '_')) + '",'
                     + 'Destino="' + unidecode.unidecode(str(df40['Destino'][d]).replace(' ', '_')) + '"'
                     + ' '
                     # Fields
                     + 'Operaciones=' + str(df40['Operaciones'][d]) + ","
                     + 'Pasajeros=' + str(df40['Pasajeros'][d])
                     + ' '
                     + str(pd.to_datetime(df40["Inicio_semana"][d]).value)
                     )
    file_writer(path, lines)


def prod41_1_to_line(df41, path):
    lines = []
    for d in range(len(df41)):
        lines.append('BIP_total'
                     + ' '
                     # Fields
                     + 'Transacciones=' + str(df41['Transacciones'][d])
                     + ' '
                     + str(pd.to_datetime(df41["Fecha"][d]).value)
                     )
    file_writer(path, lines)


def prod41_2_to_line(df41, path):
    lines = []
    # Comuna,Codigo comuna,Transacciones,Fecha
    for d in range(len(df41)):
        lines.append('BIP_comunal,'
                     # TAGS are used to check if measurements are the same
                     + 'Codigo_comuna="' + str(df41['Codigo comuna'][d]) + '",'
                     + 'Comuna="' + unidecode.unidecode(str(df41['Comuna'][d]).replace(' ', '_')) + '"'
                     + ' '
                     # Fields
                     + 'Transacciones=' + str(df41['Transacciones'][d])
                     + ' '
                     + str(pd.to_datetime(df41["Fecha"][d]).value)
                     )
    file_writer(path, lines)


def prod42_to_line(df42, path):
    lines = []
    for d in range(len(df42)):
        # Fecha,Origen,Destino,Viajes
        lines.append('Viajes_comunas,'
                     # TAGS are used to check if measurements are the same
                     + 'Origen="' + unidecode.unidecode(str(df42['Origen'][d]).replace(' ', '_')) + '",'
                     + 'Destino="' + unidecode.unidecode(str(df42['Destino'][d]).replace(' ', '_')) + '"'
                     + ' '
                     # Fields
                     + 'Viajes=' + str(df42['Viajes'][d])
                     + ' '
                     + str(pd.to_datetime(df42["Fecha"][d]).value)
                     )
    file_writer(path, lines)


# def prod43_generator(path, from_year=2019, to_year=2020):
#     # generate urls for every serie
#     particles = ['CO', 'MP10', 'MP2.5', 'NO2', 'O3', 'SO2']
#     from_year = int(from_year)
#     to_year = int(to_year)
#
#     years = [x for x in range(from_year, to_year)]
#
#     for each_particle in particles:
#         for each_year in years:
#             t0 = time.perf_counter()
#             url = GITHUB_REPO + '/producto43/' + each_particle + '-' + str(each_year) + '_std.csv'
#             print('processing ' + url)
#             df43 = pd.read_csv(url, header=[0, 1, 2, 3, 4, 5, 6], sep=',')
#             unidad = ''
#             if each_particle in ['SO2', 'NO2', 'O3']:
#                 unidad = 'partes_por_billon'
#             if each_particle in ['CO']:
#                 unidad = 'partes_por_millon'
#             if each_particle in ['MP10']:
#                 unidad = 'microgramos_por_metro_3_normalizado'
#             if each_particle in ['MP2.5']:
#                 unidad = 'microgramos_por_metro_3'
#             # print(df43)
#             # hay que recorrer por columnas (son los tags) y filas (son las observaciones por timestamp)
#             lines = []
#             for each_column in df43.columns:
#
#                 if 'Nombre de estacion' in each_column:
#                     print('Skipping')
#                     print(each_column)
#                 else:
#
#                     for each_row in df43.index:
#                         lines.append(each_particle + ','
#                                      # TAGS are used to check if measurements are the same
#                                      + 'Nombre_estacion="' + unidecode.unidecode(
#                             str(each_column[0]).replace(' ', '_')) + '",'
#                                      + 'Region="' + unidecode.unidecode(str(each_column[1]).replace(' ', '_')) + '",'
#                                      + 'Codigo_region="' + str(each_column[2]) + '",'
#                                      + 'Comuna="' + unidecode.unidecode(str(each_column[3]).replace(' ', '_')) + '",'
#                                      + 'Codigo_comuna="' + str(each_column[4]) + '",'
#                                      + 'UTM_Este="' + unidecode.unidecode(str(each_column[5])) + '",'
#                                      + 'UTM_Norte="' + unidecode.unidecode(str(each_column[6])) + '"'
#                                      + ' '
#                                      # Fields
#
#                                      + unidad + '=' + str(df43.loc[each_row, each_column])
#                                      + ' '
#                                      + str(pd.to_datetime(df43.loc[each_row, df43.columns[0]]).value)
#                                      )
#             file_writer(path + each_particle + '-' + str(each_year) + '.txt', lines)
#             t1 = time.perf_counter()
#             print('Took ' + str(t1 - t0) + ' seconds')


def prod43_generator_validate_particles(path, *my_particles, from_year=2019, to_year=2020):
    # generate urls for every serie
    valid_particles = ['CO', 'MP10', 'MP2.5', 'NO2', 'O3', 'SO2']
    from_year = int(from_year)
    to_year = int(to_year)
    # validate the particles passed are valid
    my_particles = my_particles[0]
    particles = []
    for each_my_particle in my_particles:
        if each_my_particle in valid_particles:
            print(each_my_particle + ' is valid')
            particles.append(each_my_particle)
        else:
            print('Particle ' + each_my_particle + ' unknown. Should be one of: ' + str(valid_particles))

    if len(particles) > 0:
        print('Will process ' + str(particles) + ' between ' + str(from_year) + ' and ' + str(to_year))
    else:
        print('Won\'t do anything. None of ' + str(my_particles) + ' is valid')
        return

    years = [x for x in range(from_year, to_year)]

    for each_particle in particles:
        for each_year in years:
            t0 = time.perf_counter()
            url = GITHUB_REPO + '/producto43/' + each_particle + '-' + str(each_year) + '_std.csv'
            print('processing ' + url)
            df43 = pd.read_csv(url, header=[0, 1, 2, 3, 4, 5, 6], sep=',')
            unidad = ''
            if each_particle in ['SO2', 'NO2', 'O3']:
                unidad = 'Unidad="partes_por_billon"'
            if each_particle in ['CO']:
                unidad = 'Unidad="partes_por_millon"'
            if each_particle in ['MP10']:
                unidad = 'Unidad="ugr_m_cub_normalizado"'
            if each_particle in ['MP2.5']:
                unidad = 'Unidad="ugr_m_cub"'
            # print(df43)
            df43.fillna(0, inplace=True)
            # hay que recorrer por columnas (son los tags) y filas (son las observaciones por timestamp)
            lines = []
            for each_column in df43.columns:

                if 'Nombre de estacion' not in each_column:
                    for each_row in df43.index:
                        lines.append(each_particle + ','
                                     # TAGS are used to check if measurements are the same
                                     + 'Nombre_estacion="' + unidecode.unidecode(
                            str(each_column[0]).replace(' ', '_')) + '",'
                                     + 'Region="' + unidecode.unidecode(str(each_column[1]).replace(' ', '_')) + '",'
                                     + 'Codigo_region="' + str(each_column[2]) + '",'
                                     + 'Comuna="' + unidecode.unidecode(str(each_column[3]).replace(' ', '_')) + '",'
                                     + 'Codigo_comuna="' + str(each_column[4]) + '",'
                                     + 'UTM_Este="' + unidecode.unidecode(str(each_column[5])) + '",'
                                     + 'UTM_Norte="' + unidecode.unidecode(str(each_column[6])) + '",'
                                     + unidad
                                     + ' '
                                     # Fields
                                     + 'Medicion=' + str(df43.loc[each_row, each_column])
                                     + ' '
                                     + str(pd.to_datetime(df43.loc[each_row, df43.columns[0]]).value)
                                     )
            file_writer(path + each_particle + '-' + str(each_year) + '.txt', lines)
            t1 = time.perf_counter()
            print('Took ' + str(t1 - t0) + ' seconds')


def prod44_to_line(df44, path):
    lines = []
    for d in range(len(df44)):
        # Fecha,Origen,Destino,Viajes
        lines.append('Egresos_semanales,'
                     # TAGS are used to check if measurements are the same
                     + 'Publicacion="' + unidecode.unidecode(str(df44['Egresos semanales'][d]).replace(' ', '_')) + '"'
                     + ' '
                     # Fields
                     + 'Egresos=' + str(df44['Egresos'][d])
                     + ' '
                     + str(pd.to_datetime(df44["Fecha"][d]).value)
                     )
    file_writer(path, lines)


def prod45_1_to_line(df45_1, path):
    lines = []
    df2 = pd.read_csv(
        '%s/producto45/SemanasEpidemiologicas.csv' % GITHUB_REPO)
    for d in range(len(df45_1)):
        lines.append('Casos_confirmados_comunal_FIS,'
                     # TAGS are used to check if measurements are the same
                     + 'Region="' + unidecode.unidecode(str(df45_1['Region'][d]).replace(' ', '_')) + '",'
                     + 'Codigo_region="' + str(df45_1['Codigo region'][d]) + '",'
                     + 'Comuna="' + unidecode.unidecode(str(df45_1['Comuna'][d]).replace(' ', '_')) + '",'
                     + 'Codigo_comuna="' + str(df45_1['Codigo comuna'][d]) + '",'
                     + 'Publicacion="' + str(df45_1['Publicacion'][d]) + '"'
                     + ' '
                     # Fields
                     + 'Poblacion=' + str(df45_1['Poblacion'][d]) + ","
                     + 'Casos_confirmados=' + str(df45_1['Casos confirmados'][d])
                     + ' '
                     + str(pd.to_datetime(df2.loc[[0], df45_1["Semana Epidemiologica"][d]][0]).value)
                     )
    file_writer(path, lines)


def prod45_2_to_line(df45_2, path):
    lines = []
    df2 = pd.read_csv(
        '%s/producto45/SemanasEpidemiologicas.csv' % GITHUB_REPO)
    for d in range(len(df45_2)):
        lines.append('Casos_no_notificados_comunal_FIS,'
                     # TAGS are used to check if measurements are the same
                     + 'Region="' + unidecode.unidecode(str(df45_2['Region'][d]).replace(' ', '_')) + '",'
                     + 'Codigo_region="' + str(df45_2['Codigo region'][d]) + '",'
                     + 'Comuna="' + unidecode.unidecode(str(df45_2['Comuna'][d]).replace(' ', '_')) + '",'
                     + 'Codigo_comuna="' + str(df45_2['Codigo comuna'][d]) + '",'
                     + 'Publicacion="' + str(df45_2['Publicacion'][d]) + '"'
                     + ' '
                     # Fields
                     + 'Poblacion=' + str(df45_2['Poblacion'][d]) + ","
                     + 'Casos_confirmados=' + str(df45_2['Casos no notificados'][d])
                     + ' '
                     + str(pd.to_datetime(df2.loc[[0], df45_2["Semana Epidemiologica"][d]][0]).value)
                     )
    file_writer(path, lines)


def prod45_3_to_line(df45_3, path):
    lines = []
    df2 = pd.read_csv(
        '%s/producto45/SemanasEpidemiologicas.csv' % GITHUB_REPO)
    for d in range(len(df45_3)):
        lines.append('Casos_probables_comunal_FIS,'
                     # TAGS are used to check if measurements are the same
                     + 'Region="' + unidecode.unidecode(str(df45_3['Region'][d]).replace(' ', '_')) + '",'
                     + 'Codigo_region="' + str(df45_3['Codigo region'][d]) + '",'
                     + 'Comuna="' + unidecode.unidecode(str(df45_3['Comuna'][d]).replace(' ', '_')) + '",'
                     + 'Codigo_comuna="' + str(df45_3['Codigo comuna'][d]) + '",'
                     + 'Publicacion="' + str(df45_3['Publicacion'][d]) + '"'
                     + ' '
                     # Fields
                     + 'Poblacion=' + str(df45_3['Poblacion'][d]) + ","
                     + 'Casos_confirmados=' + str(df45_3['Casos probables'][d])
                     + ' '
                     + str(pd.to_datetime(df2.loc[[0], df45_3["Semana Epidemiologica"][d]][0]).value)
                     )
    file_writer(path, lines)


def prod46_to_line(df46, path):
    lines = []
    for d in range(len(df46)):
        lines.append('Activos_vs_recuperados,'
                     # TAGS are used to check if measurements are the same
                     + 'Serie="' + unidecode.unidecode(str(df46['Casos'][d]).replace(' ', '_')) + '"'
                     + ' '
                     # Fields
                     + 'Total=' + str(df46['Total'][d])
                     + ' '
                     + str(pd.to_datetime(df46["fecha_primeros_sintomas"][d]).value)
                     )
    file_writer(path, lines)


def prod47_to_line(df47, path):
    lines = []
    for d in range(len(df47)):
        lines.append('Media_movil,'
                     # TAGS are used to check if measurements are the same
                     + 'Region="' + unidecode.unidecode(str(df47['Region'][d]).replace(' ', '_')) + '"'
                     + ' '
                     # Fields
                     + 'Media_movil=' + str(df47['Media movil'][d])
                     + ' '
                     + str(pd.to_datetime(df47["Fecha"][d]).value)
                     )
    file_writer(path, lines)


def prod48_to_line(df48, path):
    lines = []
    for d in range(len(df48)):
        lines.append('SOCHIMI,'
                     # TAGS are used to check if measurements are the same
                     + 'Region="' + unidecode.unidecode(str(df48['Region'][d]).replace(' ', '_')) + '",'
                     + 'Codigo_region="' + str(df48['Codigo region'][d]) + '",'
                     + 'Servicio_de_salud="' + unidecode.unidecode(
            str(df48['Servicio salud'][d]).replace(' ', '_')) + '"'
                     + ' '
                     # Fields
                     + 'Camas_ocupadas_intensivo=' + str(df48['Camas ocupadas intensivo'][d]).replace('-', '0') + ","
                     + 'Camas_totales_intensivo=' + str(df48['Camas totales intensivo'][d]).replace('-', '0') + ","
                     + 'Camas_ocupadas_intermedio=' + str(df48['Camas ocupadas intermedio'][d]).replace('-', '0') + ","
                     + 'Camas_totales_intermedio=' + str(df48['Camas totales intermedio'][d]).replace('-', '0') + ","
                     + 'Vmi_covid19_confirmados=' + str(df48['Vmi covid19 confirmados'][d]).replace('-', '0') + ","
                     + 'Vmi_covid19_sospechosos=' + str(df48['Vmi covid19 sospechosos'][d]).replace('-', '0') + ","
                     + 'Vmi_ocupados=' + str(df48['Vmi ocupados'][d]).replace('-', '0') + ","
                     + 'Vmi_totales=' + str(df48['Vmi totales'][d]).replace('-', '0')
                     + ' '
                     + str(pd.to_datetime(df48["Fecha"][d]).value)
                     )
    file_writer(path, lines)


def prod49_to_line(df49, path):
    lines = []
    for d in range(len(df49)):
        lines.append('Positividad,'
                     # TAGS are used to check if measurements are the same
                     + 'Serie="' + unidecode.unidecode(str(df49['Serie'][d]).replace(' ', '_')) + '"'
                     + ' '
                     # Fields
                     + 'Total=' + str(df49['Total'][d]).replace('-', '0')
                     + ' '
                     + str(pd.to_datetime(df49["Fecha"][d]).value)
                     )
    file_writer(path, lines)


#Region,Codigo region,Comuna,Codigo comuna,Poblacion,Fecha,Defunciones
def prod50_to_line(df50, path):
    lines = []
    for d in range(len(df50)):
        lines.append('Defunciones_DEIS_comunal,'
                     # TAGS are used to check if measurements are the same
                     + 'Region="' + unidecode.unidecode(str(df50['Region'][d]).replace(' ', '_')) + '",'
                     + 'Codigo_region="' + str(df50['Codigo region'][d]) + '",'
                     + 'Comuna="' + unidecode.unidecode(str(df50['Comuna'][d]).replace(' ', '_')) + '",'
                     + 'Codigo_comuna="' + str(df50['Codigo comuna'][d]) + '"'
                     + ' '
                     # Fields
                     + 'Poblacion=' + str(df50['Poblacion'][d]) + ","
                     + 'Defunciones=' + str(df50['Defunciones'][d])
                     + ' '
                     + str(pd.to_datetime(df50["Fecha"][d]).value)
                     )
    file_writer(path, lines)

def prod51_to_line(df51, path):
    lines = []
    for d in range(len(df51)):
        # Region,Codigo region,Comuna,Codigo comuna,Cartodb id,Zona censal,Week,Dif salida,Dif entrada,Fecha
        lines.append('ISCI,'
                     # TAGS are used to check if measurements are the same
                     + 'Codigo_region="' + str(df51['Codigo region'][d]) + '",'
                     + 'Region="' + unidecode.unidecode(str(df51['Region'][d]).replace(' ', '_')) + '",'
                     + 'Comuna="' + unidecode.unidecode(str(df51['Comuna'][d]).replace(' ', '_')) + '",'
                     + 'Codigo_comuna="' + str(df51['Codigo comuna'][d]).replace(' ', '_') + '",'
                     + 'Cartodb_id="' + str(df51['Cartodb id'][d]).replace(' ', '_') + '",'
                     + 'Zona_censal="' + unidecode.unidecode(str(df51['Zona censal'][d]).replace(' ', '_')) + '"'
                     + ' '
                     # Fields
                     + 'Dif_salida_min=' + str(df51['Dif salida'][d].split(',')[0].replace('[','').replace(']', '').replace('%', '').replace('+','')) + ","
                     + 'Dif_salida_max=' + str(df51['Dif salida'][d].split(',')[1].replace('[','').replace(']', '').replace('%', '').replace('+','')) + ","
                     + 'Dif_entrada_min=' + str(df51['Dif entrada'][d].split(',')[0].replace('[','').replace(']', '').replace('%', '').replace('+','')) + ","
                     + 'Dif_entrada_max=' + str(df51['Dif entrada'][d].split(',')[1].replace('[','').replace(']', '').replace('%', '').replace('+',''))
                     + ' '
                     + str(pd.to_datetime(df51["Fecha"][d]).value)
                     )
    file_writer(path, lines)

def prod52_to_line(df52, path):
    lines = []
    for d in range(len(df52)):
        lines.append('Camas_UCI,'
                     # TAGS are used to check if measurements are the same
                     + 'Serie="' + unidecode.unidecode(str(df52['Serie'][d]).replace(' ', '_')) + '",'
                     + 'Region="' + unidecode.unidecode(str(df52['Region'][d]).replace(' ', '_')) + '"'
                     + ' '
                     # Fields
                     + 'Total=' + str(df52['Casos'][d])
                     + ' '
                     + str(pd.to_datetime(df52["Fecha"][d]).value)
                     )
    file_writer(path, lines)


def csv2line(input_csv):
    if input_csv != '':
        my_df = pd.read_csv(input_csv)
        my_df = my_df.fillna(0)
        print((list(my_df)))
        if 'producto1/Covid-19_std.csv' in input_csv:
            prod1_to_line(my_df, '../output/p1-chronograf.txt')
        elif 'producto6/bulk/data.csv' in input_csv:
            prod2_to_line(my_df, '../output/p2-chronograf.txt')
        elif 'producto3/' in input_csv:
            prod3_to_line(my_df, '../output/p3-chronograf.txt')
        elif 'producto5/' in input_csv:
            prod5_to_line(my_df, '../output/p5-chronograf.txt')
        elif 'producto7/' in input_csv:
            prod7_to_line(my_df, '../output/p7-chronograf.txt')
        elif 'producto8/' in input_csv:
            prod8_to_line(my_df, '../output/p8-chronograf.txt')
        elif 'producto9/' in input_csv:
            prod9_to_line(my_df, '../output/p9-chronograf.txt')
        elif 'producto10' in input_csv:
            prod10_to_line(my_df, '../output/p10-chronograf.txt')
        elif 'producto13' in input_csv:
            prod13_to_line(my_df, '../output/p13-chronograf.txt')
        elif 'producto14' in input_csv:
            prod14_to_line(my_df, '../output/p14-chronograf.txt')
        elif 'producto15' in input_csv:
            prod15_to_line(my_df, '../output/p15-chronograf.txt')
        elif 'producto16' in input_csv:
            prod16_to_line(my_df, '../output/p16-chronograf.txt')
        elif 'producto17' in input_csv:
            prod17_to_line(my_df, '../output/p17-chronograf.txt')
        elif 'producto18' in input_csv:
            prod18_to_line(my_df, '../output/p18-chronograf.txt')
        elif 'producto19' in input_csv:
            prod19_to_line(my_df, '../output/p19-chronograf.txt')
        elif 'producto20' in input_csv:
            prod20_to_line(my_df, '../output/p20-chronograf.txt')
        # prod 21
        elif 'SintomasCasosConfirmados' in input_csv:
            prod21_1_to_line(my_df, '../output/p21_1-chronograf.txt')
        elif 'SintomasHospitalizados' in input_csv:
            prod21_2_to_line(my_df, '../output/p21_2-chronograf.txt')
        # prod 22
        elif 'HospitalizadosEtario_Acumulado' in input_csv:
            prod22_1_to_line(my_df, '../output/p22_1-chronograf.txt')
        elif 'HospitalizadosUCI_Acumulado' in input_csv:
            prod22_2_to_line(my_df, '../output/p22_2-chronograf.txt')
        elif 'producto23' in input_csv:
            prod23_to_line(my_df, '../output/p23-chronograf.txt')
        elif 'producto24' in input_csv:
            prod24_to_line(my_df, '../output/p24-chronograf.txt')
        elif 'producto25' in input_csv:
            prod25_to_line(my_df, '../output/p25-chronograf.txt')
        elif 'producto26' in input_csv:
            prod26_to_line(my_df, '../output/p26-chronograf.txt')
        elif 'producto27' in input_csv:
            prod27_to_line(my_df, '../output/p27-chronograf.txt')
        elif 'producto28' in input_csv:
            prod28_to_line(my_df, '../output/p28-chronograf.txt')
        elif 'producto30' in input_csv:
            prod30_to_line(my_df, '../output/p30-chronograf.txt')
        elif 'producto31' in input_csv:
            prod31_to_line(my_df, '../output/p31-chronograf.txt')
        elif 'producto32' in input_csv:
            prod32_to_line(my_df, '../output/p32-chronograf.txt')
        elif 'producto33' in input_csv:
            prod33_to_line(my_df, '../output/p33-chronograf.txt')
        elif 'producto35' in input_csv:
            prod35_to_line(my_df, '../output/p35-chronograf.txt')
        elif 'producto36' in input_csv:
            prod36_to_line(my_df, '../output/p36-chronograf.txt')
        elif 'producto37' in input_csv:
            prod37_to_line(my_df, '../output/p37-chronograf.txt')
        elif 'producto38' in input_csv:
            prod38_to_line(my_df, '../output/p38-chronograf.txt')
        elif 'producto39' in input_csv:
            prod39_to_line(my_df, '../output/p39-chronograf.txt')
        elif 'producto40' in input_csv:
            prod40_to_line(my_df, '../output/p40-chronograf.txt')
        elif 'BIPTotal' in input_csv:
            prod41_1_to_line(my_df, '../output/p41_1-chronograf.txt')
        elif 'BIPComuna' in input_csv:
            prod41_2_to_line(my_df, '../output/p41_2-chronograf.txt')
        elif 'producto42' in input_csv:
            prod42_to_line(my_df, '../output/p42-chronograf.txt')
        elif 'producto44' in input_csv:
            prod44_to_line(my_df, '../output/p44-chronograf.txt')
        elif 'producto45/CasosConfirmadosPorComunaHistorico_std.csv' in input_csv:
            prod45_1_to_line(my_df, '../output/p45_1-chronograf.txt')
        elif 'producto45/CasosNoNotificadosPorComunaHistorico_std.csv' in input_csv:
            prod45_2_to_line(my_df, '../output/p45_2-chronograf.txt')
        elif 'producto45/CasosProbablesPorComunaHistorico_std.csv' in input_csv:
            prod45_3_to_line(my_df, '../output/p45_3-chronograf.txt')
        elif 'producto46' in input_csv:
            prod46_to_line(my_df, '../output/p46-chronograf.txt')
        elif 'producto47' in input_csv:
            prod47_to_line(my_df, '../output/p47-chronograf.txt')
        elif 'producto48' in input_csv:
            prod48_to_line(my_df, '../output/p48-chronograf.txt')
        elif 'producto49' in input_csv:
            prod49_to_line(my_df, '../output/p49-chronograf.txt')
        elif 'producto50' in input_csv:
            prod50_to_line(my_df, '../output/p50-chronograf.txt')
        elif 'producto51' in input_csv:
            prod51_to_line(my_df, '../output/p51-chronograf.txt')
        elif 'producto52' in input_csv:
            prod52_to_line(my_df, '../output/p52-chronograf.txt')

if __name__ == '__main__':
    # run as  for i in $(seq 2010 2020); do for j in MP2.5; do python minCiencia2Influx.py $i $((${i}+1)) $j ; done &; done
    if len(sys.argv) >= 3:
        print('Generando prod43 entre ' + sys.argv[1] + ' y ' + sys.argv[2])
        prod43_generator_validate_particles('../output/p43-', sys.argv[3:], from_year=sys.argv[1], to_year=sys.argv[2])
    elif len(sys.argv) == 1:
        # print('Generando prod43 entre 2019 y 2020')
        # prod43_generator_validate_particles('../output/p43-', ['CO', 'MP10', 'MP2.5', 'NO2', 'O3', 'SO2'])
        for k in relevantCSVs:
            print('Checking ' + k + ': ' + relevantCSVs[k])
            df = csv2line(relevantCSVs[k])
