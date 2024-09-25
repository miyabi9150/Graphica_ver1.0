import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import plotly.graph_objects as go
import io
import plotly.io as pio

# image_path = './data/logo.png'
data_path = 'C:\streamlit\Graphica\data'
image_path = data_path+'\logo.png'
st.image(image_path, width=400)

# --- 0.マニュアルとサンプルデータ ---
st.markdown('<br>', unsafe_allow_html=True)  # 空白を追加
st.markdown("""##### 0. はじめての方へ""")

with st.expander("0. 使用マニュアルとサンプルデータ", expanded=False):
    st.markdown('<br>', unsafe_allow_html=True)
    st.markdown("""###### ・ マニュアルの確認""")
    # manual_path = '.\data\Graphica_manual.pdf'
    manual_path = data_path+'\Graphica_manual_ver1.0.pdf'
    st.write("以下のボタンからマニュアルをダウンロード")
    with open(manual_path, "rb") as file:
        st.download_button(
            label="Download PDF Manual",
            data=file,
            file_name="Graphica_manual.pdf",
            mime="application/pdf"
        )
    st.markdown('<br>', unsafe_allow_html=True)  
    st.markdown("""###### ・ サンプルデータのダウンロード""")
    # 埋め込みZIPファイルのパス
    # zip_file_path = '.\data\sample_data.zip'
    zip_file_path = data_path+'\sample_data.zip'
    st.write("以下のボタンからサンプルデータをダウンロード")
    with open(zip_file_path, "rb") as file:
        st.download_button(
            label="Download Sample Data",
            data=file,
            file_name="sample_data.zip",
            mime="application/zip"
        )

# --- 1.ファイルの読み込み ---
st.markdown("""<div style="padding: 20px 0;"></div>""", unsafe_allow_html=True)
st.markdown("""##### 1. データのアップロード""")
uploaded_files = st.file_uploader(
    "可視化したいファイルをアップロード [.csv, .xlsx, .xls]",
    type=["csv", "xlsx", "xls"],
    accept_multiple_files=True,
    help="[.csv, .xlsx, .xls]ファイルの読み込みが可能です"
)

if not uploaded_files:
    st.caption("※CSVファイルの文字コードはUTF-8としてください")

# --- 2.読み込みデータの表示 ---
if uploaded_files:
    dataframes = {}
    for file in uploaded_files:
        file_name = file.name.rsplit('.', 1)[0]  # 右から数えて最初の.で分割し、前部分を取得
        if file.name.endswith(".csv"):
            df = pd.read_csv(file)
        elif file.name.endswith((".xlsx", ".xls")):
            df = pd.read_excel(file)
        dataframes[file_name] = df
        
    st.markdown('<br>', unsafe_allow_html=True)
    st.markdown("""##### 2. データの確認""")
    
    with st.expander("アップロードされたデータを表示"):
        for name in sorted(dataframes.keys()):
            df = dataframes[name]
            st.write(f"{name}")
            st.dataframe(df)

    # --- 3.可視化 ---
    st.markdown("""<div style="padding: 20px 0;"></div>""", unsafe_allow_html=True)    
    st.markdown("""##### 3. グラフ可視化 """)

    if 'selected_files' not in st.session_state:
        st.session_state.selected_files = []

    selected_files = st.multiselect(
        '表示するファイルを選択してください',
        options=sorted(dataframes.keys()),
        default=st.session_state.selected_files
    )
    st.session_state.selected_files = selected_files

    col1, col2 = st.columns(2)
    with col1:
        if st.button('全選択'):
            st.session_state.selected_files = sorted(dataframes.keys())
            st.rerun()
    with col2:
        if st.button('全選択を解除'):
            st.session_state.selected_files = []
            st.rerun()

    # --- 4.カラースケールを設定 ---
    if selected_files:
        st.markdown("""<div style="padding: 20px 0;"></div>""", unsafe_allow_html=True) # 空白を追加
        st.markdown("""##### 4. グラフ描画 """)
        st.caption("※グラフの色指定が不要な場合は4-3へ（色指定しない場合、グラフカラーは自動設定）")     
        st.markdown('<br>', unsafe_allow_html=True)  # 空白を追加
        st.markdown("""###### 4-2. 色指定ファイルのアップロード（任意） """)   
        color_file = st.file_uploader(
            "作成した色指定ファイルをアップロード",
            type=["csv", "xlsx", "xls"],
            help="[.csv, .xlsx, .xls]ファイルの読み込みが可能です"
        )
        st.caption("※アップロードがない場合、各グラフのカラーは自動で設定されます")

        color_map = {}
        if color_file:
            color_df = pd.read_csv(color_file)
            for _, row in color_df.iterrows():
                color_map[row['name'].rsplit('.', 1)[0]] = row['color']  # 拡張子を除去

        if not color_map:
            default_colors = [
                '#FF0000', '#00FF00', '#0000FF', '#FFFF00', '#FF00FF', '#00FFFF', '#FFA500', '#800080', '#008000', '#FFC0CB', '#FFD700', '#00BFFF', '#FF6347', '#32CD32', '#6A5ACD', '#FF1493', '#00FF7F', '#DAA520', '#B0E0E6', '#FF4500'
            ]
        else:
            default_colors = ['#000000']

        # --- 5.グラフ設定 ---
        st.markdown('<br>', unsafe_allow_html=True)  # 空白を追加
        st.markdown("""###### 4-3. グラフの作成 """)

        if 'graph_configs' not in st.session_state:
            st.session_state.graph_configs = []

        def add_graph_config(expanded=True):
            st.session_state.graph_configs.append({
                'selected_x': None,
                'selected_y': None,
                'line_width': 0.5,
                'marker_size': 0.5,
                'plot': None,
                'expanded': expanded
            })

        def remove_graph_config(index):
            del st.session_state.graph_configs[index]
            if len(st.session_state.graph_configs) == 0:
                add_graph_config()

        # グラフ設定が空でない場合のみ新しい設定を追加
        if len(st.session_state.graph_configs) == 0:
            add_graph_config()

        for index, config in enumerate(st.session_state.graph_configs):
            with st.expander(f"グラフ設定 {index + 1}", expanded=config['expanded']):
                if selected_files:
                    selected_dfs = [dataframes[name] for name in selected_files]
                    columns = selected_dfs[0].columns.tolist()

                    selected_x = st.selectbox(f'X軸の列を選択してください（グラフ {index + 1}）', columns, key=f'x_axis_{index}', index=columns.index(config['selected_x']) if config['selected_x'] in columns else 0)
                    selected_y = st.selectbox(f'Y軸の列を選択してください（グラフ {index + 1}）', columns, key=f'y_axis_{index}', index=columns.index(config['selected_y']) if config['selected_y'] in columns else 0)

                    line_width = st.slider(
                        '線の太さを選択してください',
                        min_value=0.0,
                        max_value=10.0,
                        value=config['line_width'],
                        key=f'line_width_{index}'
                    )

                    marker_size = st.slider(
                        'マーカのサイズを選択してください',
                        min_value=0.01,
                        max_value=10.0,
                        value=config['marker_size'],
                        key=f'marker_size_{index}'
                    )

                    if st.button(f'グラフ {index + 1}を表示', key=f'plot_button_{index}'):
                        if selected_x and selected_y:  # X軸とY軸が選択されている場合のみグラフを表示
                            fig = go.Figure()

                            for idx, (df, name) in enumerate(zip(selected_dfs, selected_files)):
                                color = color_map.get(name, default_colors[idx % len(default_colors)])
                                fig.add_trace(go.Scatter(
                                    x=df[selected_x],
                                    y=df[selected_y],
                                    mode='lines+markers',
                                    name=name,
                                    line=dict(width=line_width, color=color),
                                    marker=dict(size=marker_size)
                                ))

                            fig.update_layout(
                                title=f'{selected_x} vs {selected_y}',
                                xaxis_title=selected_x,
                                yaxis_title=selected_y
                            )

                            st.session_state.graph_configs[index]['selected_x'] = selected_x
                            st.session_state.graph_configs[index]['selected_y'] = selected_y
                            st.session_state.graph_configs[index]['line_width'] = line_width
                            st.session_state.graph_configs[index]['marker_size'] = marker_size
                            st.session_state.graph_configs[index]['plot'] = fig

                            # 空の設定がある場合には追加しない
                            if all(config['selected_x'] and config['selected_y'] for config in st.session_state.graph_configs):
                                add_graph_config(expanded=False)

                    if st.button(f'グラフ設定 {index + 1} を削除', key=f'remove_button_{index}'):
                        remove_graph_config(index)

            if config['plot']:
                st.plotly_chart(config['plot'])

                # グラフをHTMLとして保存するボタン
                buffer = io.StringIO()
                pio.write_html(config['plot'], buffer)

                st.download_button(
                    label=f"HTMLをダウンロード (グラフ {index + 1})",
                    data=buffer.getvalue(),
                    file_name=f'plot_{index + 1}.html',
                    mime='text/html'
                )
                st.markdown("""<div style="padding: 10px 0;"></div>""", unsafe_allow_html=True) # 空白を追加
           
        with st.sidebar:
            st.markdown(" ### 4-1. 色指定ファイルの作成・DL（任意）")
            color_given_file = st.file_uploader(
                "色指定に用いる値を含むファイルをアップロード",
                type=["csv", "xlsx", "xls"],
                help="[.csv, .xlsx, .xls]ファイルの読み込みが可能です"
            )

            if color_given_file is not None:
                if color_given_file.name.endswith('.csv'):
                    df = pd.read_csv(color_given_file)
                elif color_given_file.name.endswith(('.xlsx', '.xls')):
                    df = pd.read_excel(color_given_file)
                
                # カラーマップの設定
                cmap = plt.get_cmap('rainbow')

                # カラーマップに基づく値の正規化
                norm = mcolors.Normalize(vmin=df['value'].min(), vmax=df['value'].max())
                df['color'] = df['value'].apply(lambda x: mcolors.to_hex(cmap(norm(x))))

                # カラーマップの表示
                st.markdown(" #### < カラースケールの表示 >")
                fig, ax = plt.subplots(figsize=(6, 1))
                fig.subplots_adjust(bottom=0.5)
                
                # カラーバーの描画
                cb = plt.colorbar(
                    plt.cm.ScalarMappable(norm=norm, cmap=cmap),
                    cax=ax,
                    orientation='horizontal'
                )
                cb.set_label('Value')
                st.pyplot(fig)

                # DataFrameの表示（小数点以下の桁数を適切に表示）
                st.dataframe(df.style.format({'value': "{:g}"}).applymap(lambda color: f'background-color: {color}', subset=['color']))


                # DataFrameをCSVファイルとしてダウンロードするボタン
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Download CSV (color_scale.csv)",
                    data=csv,
                    file_name='color_scale.csv',
                    mime='text/csv'
                )