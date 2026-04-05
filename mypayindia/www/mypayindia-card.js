class MyPayIndiaCard extends HTMLElement {
  setConfig(config) {
    this.config = config;
    if (!this.content) {
      this.innerHTML = `
        <ha-card header="MyPayIndia Transfer">
          <div class="card-content" style="display: flex; flex-direction: column; gap: 16px;">
            <ha-textfield id="recipient" label="Recipient"></ha-textfield>
            <ha-textfield id="amount" label="Amount (INR)" type="number"></ha-textfield>
            <ha-textfield id="note" label="Note (Optional)"></ha-textfield>
            <mwc-button id="send" raised label="Send Money"></mwc-button>
          </div>
        </ha-card>
      `;
      this.content = true;

      this.querySelector('#send').addEventListener('click', () => {
        const recipient = this.querySelector('#recipient').value;
        const amount = this.querySelector('#amount').value;
        const note = this.querySelector('#note').value;

        if (recipient && amount) {
            this._hass.callService('mypayindia', 'transfer', {
                recipient: recipient,
                amount: parseFloat(amount),
                note: note
            });

            this.querySelector('#recipient').value = '';
            this.querySelector('#amount').value = '';
            this.querySelector('#note').value = '';
        }
      });
    }
  }

  set hass(hass) {
    this._hass = hass;
  }
}

customElements.define('mypayindia-card', MyPayIndiaCard);

window.customCards = window.customCards || [];
window.customCards.push({
  type: "mypayindia-card",
  name: "MyPayIndia Transfer Card",
  description: "A custom UI for sending money via MyPayIndia."
});