from ...schemas import BrokerData


def build_quotation_broker(broker_details: dict) -> BrokerData:
    # Broker
    broker_data = BrokerData(
        name=broker_details.get("trade_name") or broker_details.get("preferred_name") or "Não informado",
        susep="",
        commission_pct="0.0%",
        phone=broker_details.get("phone") or "Não informado",
        emails=[broker_details.get("email") or "Não informado"],
        phones=[broker_details.get("phone") or "Não informado"],
    )

    return broker_data


def build_proposal_broker(broker_details: dict) -> BrokerData:
    # Broker
    broker_data = BrokerData(
        name=broker_details.get("trade_name") or broker_details.get("preferred_name") or "Não informado",
        susep="",
        commission_pct="0.0%",
        phone=broker_details.get("phone") or "Não informado",
        emails=[broker_details.get("email") or "Não informado"],
        phones=[broker_details.get("phone") or "Não informado"],
    )

    return broker_data