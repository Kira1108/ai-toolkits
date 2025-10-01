from typing import Optional

from pydantic import BaseModel, Field

from ai_toolkits.llms.openai_provider import (create_async_client,
                                              create_sync_client)

from ai_toolkits.structured import (acreate_object_openai_safe,
                                    create_object_openai)


class NormalizedAddress(BaseModel):
    """
    An normalized address is an address that can be used in downstream tasks or searchable databases, map apis, etc.
    
    Your strategy: you can use referenced addresses to fill in the missing parts of the input address, and output a complete standardized address.
    
    You are trying your best to fill all the parts of this schema.
    
    Some or which are extracted from the input address, and some or which are inferred from the referenced addresses.
    Try to fill as many fields as possible.
    """
    country: Optional[str] = Field(default = "中国", description="国家")
    province: Optional[str] = Field(default = None, description="省份")
    city: Optional[str] = Field(default = None, description="城市")
    district: Optional[str] = Field(default = None, description="区县")
    street: Optional[str] = Field(default = None, description="街道")
    house_number: Optional[str] = Field(default = None, description="门牌号")
    postal_code: Optional[str] = Field(default = None, description="邮编")
    normalize_address: Optional[str] = Field(default = None, description="标准化地址, 如果有相似地点的参考地址，按照参考地址进行标准化")
    

class AddressNormalizer:
    
    """
    Example Usage:
    
    ```python
    from ai_toolkits.applications.address_normalizer import AddressNormalizer, NormalizedAddress

    reference_address1 = NormalizedAddress(
        country="中国",
        province="北京市",
        city="北京市",
        district="朝阳区",
        street="幸福路",
        house_number="33号",
        postal_code="100020",
        normalize_address="北京市朝阳区幸福路33号天地大厦B座希望幼儿园"
    )

    reference_address2 = NormalizedAddress(
        country="中国",
        province="天津市",
        city="天津市",
        district="和平区",
        street="经纬路",
        house_number="99号",
        postal_code="300010",
        normalize_address="天津市和平区经纬路99号津塔大厦"
    )

    reference_address3 = NormalizedAddress(
        country="中国",
        province="上海市",
        city="上海市",
        district="浦东新区",
        street="世纪大道",
        house_number="100号",
        postal_code="200120",
        normalize_address="上海市浦东新区世纪大道100号环球金融中心"
    )


    address = "我在天地大厦A座1203室,快来救我"
    normalizer = AddressNormalizer()


    await normalizer.normalize_async(address, [reference_address1, reference_address2, reference_address3])


    >>> NormalizedAddress(
        country='中国',
        province='北京市', 
        city='北京市', 
        district='朝阳区', 
        street='幸福路', 
        house_number='33号天地大厦A座1203室', 
        postal_code='100020',
        normalize_address='北京市朝阳区幸福路33号天地大厦A座1203室'
        )
    ```
    
    """
    
    def __init__(self, client = None, async_client = None):
        self.client = client or create_sync_client()
        self.async_client = async_client or create_async_client()

    def normalize(self, address: str, reference_address: list[NormalizedAddress]) -> NormalizedAddress:
        rag_content = "\n".join([addr.model_dump_json() for addr in reference_address])
        prompt =f"Given some similar addresses: \n {rag_content}\n Normalize this address: \n {address}\n. [do your best to fill as many fields as possible]"
        res = create_object_openai(
            output_cls=NormalizedAddress,
            prompt=prompt,
            client=self.client
        )
        return res
    
    async def normalize_async(self,
                              address: str, 
                              reference_address: list[NormalizedAddress]) -> NormalizedAddress:
        
        rag_content = "\n".join([addr.model_dump_json() for addr in reference_address])
        prompt =f"Given some similar addresses: \n {rag_content}\n Normalize this address: \n {address}\n. [do your best to fill as many fields as possible]"
        res = await acreate_object_openai_safe(
            output_cls=NormalizedAddress,
            prompt=prompt,
            client=self.async_client
        )
        return res