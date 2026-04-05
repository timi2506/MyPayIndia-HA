class MyPayIndiaTransferCard extends HTMLElement {
  setConfig(config) {
    this.config = config;
    if (!this.content) {
      this.innerHTML = `
        <ha-card header="MyPayIndia - Send Money">
          <div class="card-content" style="display: flex; flex-direction: column; gap: 16px;">
            <ha-textfield id="recipient" label="Recipient Username"></ha-textfield>
            <ha-textfield id="amount" label="Amount (INR)" type="number"></ha-textfield>
            <ha-textfield id="note" label="Note (Optional)"></ha-textfield>
            <ha-button raised id="send" style="width: 100%; justify-content: center;">Send Money</ha-button>
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

class MyPayIndiaCreateLinkCard extends HTMLElement {
  setConfig(config) {
    this.config = config;
    if (!this.content) {
      this.innerHTML = `
        <ha-card header="Create Payment Link">
          <div class="card-content" style="display: flex; flex-direction: column; gap: 16px;">
            <ha-textfield id="link_amount" label="Amount (INR)" type="number"></ha-textfield>
            <ha-textfield id="link_note" label="Note (Optional)"></ha-textfield>
            <ha-button raised id="create_link" style="width: 100%; justify-content: center;">Create Link</ha-button>
          </div>
        </ha-card>
      `;
      this.content = true;

      this.querySelector('#create_link').addEventListener('click', () => {
        const amount = this.querySelector('#link_amount').value;
        const note = this.querySelector('#link_note').value;

        if (amount) {
            this._hass.callService('mypayindia', 'create_payment_link', {
                amount: parseFloat(amount),
                note: note
            });

            this.querySelector('#link_amount').value = '';
            this.querySelector('#link_note').value = '';
        }
      });
    }
  }
  set hass(hass) {
    this._hass = hass;
  }
}

class MyPayIndiaLinksCard extends HTMLElement {
  setConfig(config) {
    this.config = config;
    this.entityId = config.entity || null;
  }
  set hass(hass) {
    this._hass = hass;
    if (!this.entityId) {
        this.entityId = Object.keys(hass.states).find(eid => eid.startsWith('sensor.mypayindia_total_active_links'));
    }
    const stateObj = hass.states[this.entityId];
    if (!stateObj) return;

    if (!this.content) {
        this.innerHTML = `
          <ha-card>
              <div style="display: flex; justify-content: space-between; align-items: center; padding: 24px 16px 16px 16px;">
                  <div style="font-size: 20px; font-weight: 400; color: var(--ha-card-header-color, var(--primary-text-color));">Active Payment Links</div>
                  <ha-icon icon="mdi:refresh" id="refresh_links" style="cursor: pointer; color: var(--secondary-text-color);"></ha-icon>
              </div>
              <div class="card-content" id="links-container" style="display: flex; flex-direction: column; gap: 12px; padding-top: 0;"></div>
          </ha-card>
        `;
        this.content = true;
        this.querySelector('#refresh_links').addEventListener('click', () => {
            this._hass.callService('homeassistant', 'update_entity', { entity_id: this.entityId });
        });
    }

    const links = stateObj.attributes.links || [];
    let html = '';
    
    if (links.length === 0) {
        html = `<p style="color: var(--secondary-text-color);">No active payment links.</p>`;
    } else {
        links.forEach(link => {
            html += `
            <div style="padding: 12px; border: 1px solid var(--divider-color); border-radius: 8px;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                    <strong style="font-size: 1.1em;">${link.amount} INR</strong>
                    <span style="color: var(--secondary-text-color);">${link.status}</span>
                </div>
                ${link.note ? `<div style="margin-bottom: 8px;"><em>"${link.note}"</em></div>` : ''}
                <div style="font-size: 0.9em; word-break: break-all;">
                    <a href="${link.claim_url}" target="_blank" style="color: var(--primary-color); text-decoration: none;">${link.claim_url}</a>
                </div>
            </div>`;
        });
    }
    
    this.querySelector('#links-container').innerHTML = html;
  }
}

class MyPayIndiaHistoryCard extends HTMLElement {
  setConfig(config) {
    this.config = config;
    this.entityId = config.entity || null;
    this.balanceEntityId = null;
  }
  set hass(hass) {
    this._hass = hass;
    if (!this.entityId) {
        this.entityId = Object.keys(hass.states).find(eid => eid.startsWith('sensor.mypayindia_total_transferred'));
    }
    if (!this.balanceEntityId) {
        this.balanceEntityId = Object.keys(hass.states).find(eid => eid.startsWith('sensor.mypayindia_balance'));
    }

    const stateObj = hass.states[this.entityId];
    const balanceObj = hass.states[this.balanceEntityId];
    if (!stateObj || !balanceObj) return;

    if (!this.content) {
        this.innerHTML = `
          <ha-card>
              <div style="display: flex; justify-content: space-between; align-items: center; padding: 24px 16px 16px 16px;">
                  <div style="font-size: 20px; font-weight: 400; color: var(--ha-card-header-color, var(--primary-text-color));">Transaction History</div>
                  <ha-icon icon="mdi:refresh" id="refresh_history" style="cursor: pointer; color: var(--secondary-text-color);"></ha-icon>
              </div>
              <div class="card-content" id="history-container" style="display: flex; flex-direction: column; gap: 8px; padding-top: 0;"></div>
          </ha-card>
        `;
        this.content = true;
        this.querySelector('#refresh_history').addEventListener('click', () => {
            this._hass.callService('homeassistant', 'update_entity', { entity_id: this.entityId });
        });
    }

    const txns = stateObj.attributes.transactions || [];
    const myUsername = balanceObj.attributes.username;
    let html = '';
    
    if (txns.length === 0) {
        html = `<p style="color: var(--secondary-text-color);">No recent transactions.</p>`;
    } else {
        txns.forEach(txn => {
            const isSender = txn.sender_name === myUsername;
            const amountColor = isSender ? 'var(--error-color)' : 'var(--success-color)';
            const amountPrefix = isSender ? '-' : '+';
            const relatedUser = isSender ? `To: ${txn.target_name}` : `From: ${txn.sender_name}`;
            const date = new Date(txn.created).toLocaleString();

            html += `
            <div style="display: flex; justify-content: space-between; align-items: center; padding: 8px 0; border-bottom: 1px solid var(--divider-color);">
                <div style="display: flex; flex-direction: column;">
                    <strong>${relatedUser}</strong>
                    <span style="font-size: 0.8em; color: var(--secondary-text-color);">${date}</span>
                </div>
                <div style="font-weight: bold; color: ${amountColor};">
                    ${amountPrefix}${txn.amount} INR
                </div>
            </div>`;
        });
    }
    
    this.querySelector('#history-container').innerHTML = html;
  }
}

class MyPayIndiaBalanceCard extends HTMLElement {
  setConfig(config) {
    this.config = config;
    this.entityId = config.entity || null;
  }
  set hass(hass) {
    this._hass = hass;
    if (!this.entityId) {
        this.entityId = Object.keys(hass.states).find(eid => eid.startsWith('sensor.mypayindia_balance'));
    }
    const stateObj = hass.states[this.entityId];
    if (!stateObj) return;

    if (!this.content) {
        this.innerHTML = `
          <ha-card>
            <div style="display: flex; justify-content: flex-end; padding: 16px 16px 0 16px;">
                <ha-icon icon="mdi:refresh" id="refresh_balance" style="cursor: pointer; color: var(--secondary-text-color);"></ha-icon>
            </div>
            <div class="card-content" style="text-align: center; padding: 0 16px 32px 16px;">
                <div style="font-size: 1.2em; color: var(--secondary-text-color); margin-bottom: 8px;">Available Balance</div>
                <div style="font-size: 3em; font-weight: bold; color: var(--primary-text-color);">
                    <span id="balance_amount"></span> <span style="font-size: 0.5em; color: var(--secondary-text-color);">INR</span>
                </div>
                <div style="margin-top: 16px; font-size: 0.9em; color: var(--secondary-text-color);" id="account_details"></div>
            </div>
          </ha-card>
        `;
        this.content = true;
        this.querySelector('#refresh_balance').addEventListener('click', () => {
            this._hass.callService('homeassistant', 'update_entity', { entity_id: this.entityId });
        });
    }

    this.querySelector('#balance_amount').innerText = stateObj.state;
    this.querySelector('#account_details').innerText = `Account: ${stateObj.attributes.first_name} ${stateObj.attributes.last_name} (@${stateObj.attributes.username})`;
  }
}

customElements.define('mypayindia-transfer-card', MyPayIndiaTransferCard);
customElements.define('mypayindia-create-link-card', MyPayIndiaCreateLinkCard);
customElements.define('mypayindia-links-card', MyPayIndiaLinksCard);
customElements.define('mypayindia-history-card', MyPayIndiaHistoryCard);
customElements.define('mypayindia-balance-card', MyPayIndiaBalanceCard);

window.customCards = window.customCards || [];
window.customCards.push(
  { type: "mypayindia-transfer-card", name: "MyPayIndia Transfer", description: "Send money via MyPayIndia" },
  { type: "mypayindia-create-link-card", name: "MyPayIndia Create Link", description: "Create a payment link" },
  { type: "mypayindia-links-card", name: "MyPayIndia Links", description: "Active payment links" },
  { type: "mypayindia-history-card", name: "MyPayIndia History", description: "Transaction history" },
  { type: "mypayindia-balance-card", name: "MyPayIndia Balance", description: "Current balance" }
);