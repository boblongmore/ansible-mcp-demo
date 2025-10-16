import streamlit as st
from PIL import Image
import logging
from fw_client import analyze_sync, main


def st_chat_interface():
    """ starts streamlit app and awaits input"""
    icon_path = "images/pete-3d.png"
    icon_image = Image.open(icon_path)
    col1, col2 = st.columns([1, 5])  # Adjust the proportions as needed

    # Place the icon in the first column and the title in the second column
    with col1:
        st.image(icon_image, width=100)  # Adjust the width as needed
    with col2:
        st.title("It's Not The Firewall!")
    with st.form("my_form"):
        text = st.text_area(
            "Provide the source, destination, and port if possible",
            "Type your query here",
        )
        submitted = st.form_submit_button("Submit")
        if submitted:
            # Prefer the synchronous helper. If the environment already has an
            # event loop (rare in Streamlit), analyze_sync may raise a
            # RuntimeError; in that case run the async main in a new thread.
            try:
                resp = analyze_sync(text)
            except RuntimeError:
                import asyncio
                import threading

                def run_coro_in_thread(coro, *args):
                    loop = asyncio.new_event_loop()
                    result = {}

                    def _run():
                        asyncio.set_event_loop(loop)
                        result['value'] = loop.run_until_complete(coro(*args))
                        loop.close()

                    t = threading.Thread(target=_run)
                    t.start()
                    t.join()
                    return result.get('value')

                resp = run_coro_in_thread(main, text)

            st.info(resp)


if __name__ == "__main__":
    st_chat_interface()
